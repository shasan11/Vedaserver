# reviews/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q

from core.utils.coreModels import StampedOwnedActive, BranchScopedStampedOwnedActive


# ----------------------------- choices -----------------------------

class ReviewStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    HIDDEN = "hidden", "Hidden"  # approved earlier but later hidden/moderated


class ReportReason(models.TextChoices):
    SPAM = "spam", "Spam"
    HARASSMENT = "harassment", "Harassment"
    HATE = "hate", "Hate speech"
    FALSE_INFO = "false_info", "False information"
    OTHER = "other", "Other"


class ReportStatus(models.TextChoices):
    OPEN = "open", "Open"
    REVIEWED = "reviewed", "Reviewed"
    DISMISSED = "dismissed", "Dismissed"


# ----------------------------- course review -----------------------------

class CourseReview(BranchScopedStampedOwnedActive):
    """
    One review per user per course (active).
    Use status moderation for approval workflows.
    """

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="reviews",
        db_index=True,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="course_reviews",
        db_index=True,
    )

    # optional: tie review to the enrollment that gave them access
    enrollment = models.ForeignKey(
        "enrollments.Enrollment",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reviews",
        db_index=True,
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        db_index=True,
    )

    title = models.CharField(max_length=180, blank=True, null=True)
    body = models.TextField(blank=True, null=True)

    is_anonymous = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
        db_index=True,
    )

    approved_at = models.DateTimeField(blank=True, null=True, db_index=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="reviews_approved",
    )

    rejected_at = models.DateTimeField(blank=True, null=True)
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="reviews_rejected",
    )
    reject_reason = models.TextField(blank=True, null=True)

    edited_at = models.DateTimeField(blank=True, null=True)

    # denormalized (updated by service/signal)
    helpful_count = models.PositiveIntegerField(default=0)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "course_reviews"
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["course", "status"]),
            models.Index(fields=["course", "rating"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["user", "created"]),
        ]
        constraints = [
            # One active review per user per course (prevents duplicates)
            models.UniqueConstraint(
                fields=["course", "user"],
                condition=Q(status__in=[ReviewStatus.PENDING, ReviewStatus.APPROVED, ReviewStatus.HIDDEN]),
                name="uniq_active_review_course_user",
            )
        ]

    def __str__(self):
        return f"Review({self.course_id}::{self.user_id}::{self.rating})"

    def save(self, *args, **kwargs):
        # keep branch consistent with course
        if self.course_id and self.branch_id is None:
            self.branch = self.course.branch
        super().save(*args, **kwargs)

    def approve(self, by_user=None):
        self.status = ReviewStatus.APPROVED
        self.approved_at = timezone.now()
        self.approved_by = by_user
        self.save(update_fields=["status", "approved_at", "approved_by", "updated"])

    def reject(self, by_user=None, reason=None):
        self.status = ReviewStatus.REJECTED
        self.rejected_at = timezone.now()
        self.rejected_by = by_user
        self.reject_reason = reason
        self.save(update_fields=["status", "rejected_at", "rejected_by", "reject_reason", "updated"])

    def hide(self, by_user=None, reason=None):
        self.status = ReviewStatus.HIDDEN
        self.meta = self.meta or {}
        if reason:
            self.meta["hidden_reason"] = reason
        if by_user:
            self.meta["hidden_by"] = str(by_user.id)
        self.save(update_fields=["status", "meta", "updated"])


# ----------------------------- instructor reply -----------------------------

class ReviewReply(StampedOwnedActive):
    """
    Instructor/staff replies to a review.
    """

    review = models.ForeignKey(CourseReview, on_delete=models.CASCADE, related_name="replies", db_index=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="review_replies",
        db_index=True,
    )

    message = models.TextField()

    is_official = models.BooleanField(default=True)

    class Meta:
        db_table = "review_replies"
        ordering = ["created"]
        indexes = [
            models.Index(fields=["review", "created"]),
            models.Index(fields=["author", "created"]),
        ]

    def __str__(self):
        return f"Reply({self.review_id})"


# ----------------------------- helpful votes / reactions -----------------------------

class ReviewReactionType(models.TextChoices):
    HELPFUL = "helpful", "Helpful"
    NOT_HELPFUL = "not_helpful", "Not helpful"


class ReviewReaction(StampedOwnedActive):
    """
    Prevents "spam likes" and allows helpful_count calculation.
    """

    review = models.ForeignKey(CourseReview, on_delete=models.CASCADE, related_name="reactions", db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="review_reactions", db_index=True)

    reaction_type = models.CharField(max_length=20, choices=ReviewReactionType.choices, default=ReviewReactionType.HELPFUL, db_index=True)

    class Meta:
        db_table = "review_reactions"
        constraints = [
            models.UniqueConstraint(fields=["review", "user"], name="uniq_review_user_reaction")
        ]
        indexes = [
            models.Index(fields=["review", "reaction_type"]),
            models.Index(fields=["user", "created"]),
        ]

    def __str__(self):
        return f"Reaction({self.review_id}::{self.user_id})"


# ----------------------------- reports / abuse -----------------------------

class ReviewReport(StampedOwnedActive):
    """
    Users can report abusive/spam reviews.
    """

    review = models.ForeignKey(CourseReview, on_delete=models.CASCADE, related_name="reports", db_index=True)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="review_reports", db_index=True)

    reason = models.CharField(max_length=20, choices=ReportReason.choices, default=ReportReason.OTHER, db_index=True)
    details = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=ReportStatus.choices, default=ReportStatus.OPEN, db_index=True)

    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="review_reports_reviewed",
    )
    resolution_note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "review_reports"
        constraints = [
            models.UniqueConstraint(fields=["review", "reported_by"], name="uniq_review_reporter")
        ]
        indexes = [
            models.Index(fields=["status", "created"]),
            models.Index(fields=["review", "status"]),
        ]

    def __str__(self):
        return f"Report({self.review_id}::{self.status})"


# ----------------------------- optional: rating breakdown (fast stats) -----------------------------

class CourseRatingSummary(BranchScopedStampedOwnedActive):
    """
    Denormalized rating breakdown per course (optional).
    Useful for fast UI without heavy aggregation queries.
    Update via signals/services when reviews change status.
    """

    course = models.OneToOneField("courses.Course", on_delete=models.CASCADE, related_name="rating_summary")

    rating_1 = models.PositiveIntegerField(default=0)
    rating_2 = models.PositiveIntegerField(default=0)
    rating_3 = models.PositiveIntegerField(default=0)
    rating_4 = models.PositiveIntegerField(default=0)
    rating_5 = models.PositiveIntegerField(default=0)

    total_reviews = models.PositiveIntegerField(default=0, db_index=True)
    average_rating = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    class Meta:
        db_table = "course_rating_summaries"
        indexes = [
            models.Index(fields=["branch", "total_reviews"]),
        ]

    def __str__(self):
        return f"RatingSummary({self.course_id})"

    def save(self, *args, **kwargs):
        if self.course_id and self.branch_id is None:
            self.branch = self.course.branch
        super().save(*args, **kwargs)
