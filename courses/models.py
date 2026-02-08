# courses/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from core.utils.coreModels import (
    StampedOwnedActive,
    BranchScopedStampedOwnedActive,
)


# ----------------------------- choices -----------------------------

class CourseStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    IN_REVIEW = "in_review", "In Review"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class CourseVisibility(models.TextChoices):
    PUBLIC = "public", "Public"
    UNLISTED = "unlisted", "Unlisted (link only)"
    PRIVATE = "private", "Private (members only)"


class CourseLevel(models.TextChoices):
    BEGINNER = "beginner", "Beginner"
    INTERMEDIATE = "intermediate", "Intermediate"
    ADVANCED = "advanced", "Advanced"
    ALL = "all", "All Levels"


class InstructorRole(models.TextChoices):
    OWNER = "owner", "Owner"
    CO_INSTRUCTOR = "co_instructor", "Co-instructor"
    ASSISTANT = "assistant", "Assistant"


class PricingType(models.TextChoices):
    FREE = "free", "Free"
    PAID = "paid", "Paid"


# ----------------------------- taxonomy -----------------------------

class CourseCategory(BranchScopedStampedOwnedActive):
    """
    Category tree. Use parent for sub-categories.
    (You can keep branch NULL if you want shared/global categories.)
    """

    name = models.CharField(max_length=120, db_index=True)
    slug = models.SlugField(max_length=140, db_index=True)

    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="children",
        blank=True,
        null=True,
    )

    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=80, blank=True, null=True)  # optional: icon name
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "course_categories"
        ordering = ["sort_order", "name"]
        constraints = [
            # same slug can exist in different branches, but not within same branch
            models.UniqueConstraint(fields=["branch", "slug"], name="uniq_course_category_branch_slug")
        ]
        indexes = [
            models.Index(fields=["branch", "active"]),
            models.Index(fields=["parent"]),
        ]

    def __str__(self):
        return self.name


class CourseTag(BranchScopedStampedOwnedActive):
    name = models.CharField(max_length=80, db_index=True)
    slug = models.SlugField(max_length=100, db_index=True)

    class Meta:
        db_table = "course_tags"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["branch", "slug"], name="uniq_course_tag_branch_slug")
        ]
        indexes = [
            models.Index(fields=["branch", "active"]),
        ]

    def __str__(self):
        return self.name


# ----------------------------- course core -----------------------------

class Course(BranchScopedStampedOwnedActive):
    """
    Course metadata/catalog. NOT lessons/modules (put that in content app).
    """

    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, db_index=True)

    subtitle = models.CharField(max_length=255, blank=True, null=True)

    # marketing / catalog
    short_description = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)  # rich text stored as HTML/MD if you want

    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.PROTECT,
        related_name="courses",
        blank=True,
        null=True,
    )

    tags = models.ManyToManyField(
        CourseTag,
        through="CourseTagging",
        related_name="courses",
        blank=True,
    )

    # basic attributes
    language = models.CharField(max_length=10, default="en", db_index=True)
    level = models.CharField(max_length=20, choices=CourseLevel.choices, default=CourseLevel.ALL, db_index=True)

    estimated_duration_minutes = models.PositiveIntegerField(default=0)  # optional estimate

    # media
    thumbnail_url = models.URLField(blank=True, null=True)
    promo_video_url = models.URLField(blank=True, null=True)

    # access + publishing
    status = models.CharField(max_length=20, choices=CourseStatus.choices, default=CourseStatus.DRAFT, db_index=True)
    visibility = models.CharField(max_length=20, choices=CourseVisibility.choices, default=CourseVisibility.PUBLIC, db_index=True)

    published_at = models.DateTimeField(blank=True, null=True, db_index=True)
    archived_at = models.DateTimeField(blank=True, null=True)

    # cohort-style optional (ignore if you’re async-only)
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)

    # capacity (optional)
    max_students = models.PositiveIntegerField(blank=True, null=True)

    # SEO
    seo_title = models.CharField(max_length=70, blank=True, null=True)
    seo_description = models.CharField(max_length=160, blank=True, null=True)

    # knobs
    allow_reviews = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, db_index=True)

    # denormalized stats (keep updated by signals/jobs later)
    enrollment_count = models.PositiveIntegerField(default=0)
    rating_avg = models.DecimalField(max_digits=4, decimal_places=2, default=0)   # 0.00 - 5.00
    rating_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "courses"
        ordering = ["-published_at", "-created"]
        constraints = [
            models.UniqueConstraint(fields=["branch", "slug"], name="uniq_course_branch_slug"),
        ]
        indexes = [
            models.Index(fields=["branch", "status", "active"]),
            models.Index(fields=["category"]),
            models.Index(fields=["status", "visibility"]),
            models.Index(fields=["is_featured", "published_at"]),
        ]

    def __str__(self):
        return self.title

    def publish(self):
        self.status = CourseStatus.PUBLISHED
        if not self.published_at:
            self.published_at = timezone.now()
        self.save(update_fields=["status", "published_at"])

    def archive(self):
        self.status = CourseStatus.ARCHIVED
        self.archived_at = timezone.now()
        self.save(update_fields=["status", "archived_at"])


class CourseTagging(StampedOwnedActive):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="tag_links")
    tag = models.ForeignKey(CourseTag, on_delete=models.CASCADE, related_name="course_links")

    class Meta:
        db_table = "course_taggings"
        constraints = [
            models.UniqueConstraint(fields=["course", "tag"], name="uniq_course_tag")
        ]


# ----------------------------- instructors (many-to-many) -----------------------------

class CourseInstructor(StampedOwnedActive):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="instructors")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="teaching_courses",
    )

    role = models.CharField(max_length=20, choices=InstructorRole.choices, default=InstructorRole.CO_INSTRUCTOR, db_index=True)
    is_primary = models.BooleanField(default=False, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)

    # optional overrides for display (if you want custom name/headline per course)
    display_name = models.CharField(max_length=150, blank=True, null=True)
    headline = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = "course_instructors"
        ordering = ["sort_order", "-is_primary"]
        constraints = [
            models.UniqueConstraint(fields=["course", "user"], name="uniq_course_instructor"),
        ]
        indexes = [
            models.Index(fields=["course", "is_primary"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.user_id} -> {self.course_id}"


# ----------------------------- pricing -----------------------------

class CoursePricing(StampedOwnedActive):
    """
    One-to-one pricing record so you can evolve later without bloating Course.
    """

    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name="pricing")

    pricing_type = models.CharField(max_length=10, choices=PricingType.choices, default=PricingType.FREE, db_index=True)

    # Prefer FK if you already have settings.Currency model, else keep char
    currency_code = models.CharField(max_length=3, default="NPR", db_index=True)

    price = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    sale_price = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])

    sale_start_at = models.DateTimeField(blank=True, null=True)
    sale_end_at = models.DateTimeField(blank=True, null=True)

    tax_included = models.BooleanField(default=False)
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        db_table = "course_pricing"
        indexes = [
            models.Index(fields=["pricing_type"]),
            models.Index(fields=["currency_code"]),
        ]

    def __str__(self):
        return f"Pricing({self.course_id})"

    def effective_price(self):
        """
        Returns sale_price if within sale window; else price.
        """
        if self.pricing_type == PricingType.FREE:
            return 0

        now = timezone.now()
        if self.sale_price is not None:
            if (self.sale_start_at is None or self.sale_start_at <= now) and (self.sale_end_at is None or now <= self.sale_end_at):
                return self.sale_price
        return self.price


# ----------------------------- inline-friendly marketing blocks -----------------------------

class CourseOutcome(StampedOwnedActive):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="outcomes")
    text = models.CharField(max_length=255)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "course_outcomes"
        ordering = ["sort_order", "id"]
        indexes = [models.Index(fields=["course"])]

    def __str__(self):
        return self.text


class CourseRequirement(StampedOwnedActive):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="requirements")
    text = models.CharField(max_length=255)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "course_requirements"
        ordering = ["sort_order", "id"]
        indexes = [models.Index(fields=["course"])]

    def __str__(self):
        return self.text


class CourseTargetAudience(StampedOwnedActive):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="target_audience")
    text = models.CharField(max_length=255)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "course_target_audience"
        ordering = ["sort_order", "id"]
        indexes = [models.Index(fields=["course"])]

    def __str__(self):
        return self.text


class CourseFAQ(StampedOwnedActive):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(max_length=255)
    answer = models.TextField(blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "course_faqs"
        ordering = ["sort_order", "id"]
        indexes = [models.Index(fields=["course"])]

    def __str__(self):
        return self.question


# ----------------------------- review/publish workflow (optional but powerful) -----------------------------

class CourseReviewStatus(models.TextChoices):
    REQUESTED = "requested", "Requested"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class CourseReview(StampedOwnedActive):
    """
    For "submit for review" flows.
    Keeps an audit trail of approvals/rejections.
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")

    status = models.CharField(max_length=20, choices=CourseReviewStatus.choices, default=CourseReviewStatus.REQUESTED, db_index=True)

    requested_at = models.DateTimeField(default=timezone.now, db_index=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="course_review_requests",
        blank=True,
        null=True,
    )

    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="course_reviews_done",
        blank=True,
        null=True,
    )

    note = models.TextField(blank=True, null=True)  # rejection reason / feedback

    class Meta:
        db_table = "course_reviews"
        indexes = [
            models.Index(fields=["course", "status"]),
            models.Index(fields=["status", "requested_at"]),
        ]

    def __str__(self):
        return f"Review({self.course_id}, {self.status})"
