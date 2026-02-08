# content/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from core.utils.coreModels import (
    StampedOwnedActive,
    BranchScopedStampedOwnedActive,
)


# ----------------------------- choices -----------------------------

class ModuleVisibility(models.TextChoices):
    PUBLIC = "public", "Public"
    ENROLLED_ONLY = "enrolled_only", "Enrolled Only"
    PRIVATE = "private", "Private"


class LessonStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class LessonType(models.TextChoices):
    VIDEO = "video", "Video"
    ARTICLE = "article", "Article"
    FILE = "file", "File / Download"
    QUIZ = "quiz", "Quiz"
    ASSIGNMENT = "assignment", "Assignment"
    LIVE = "live", "Live Class"
    EXTERNAL = "external", "External Link"


class ContentFormat(models.TextChoices):
    HTML = "html", "HTML"
    MARKDOWN = "markdown", "Markdown"
    BLOCKS = "blocks", "Blocks (JSON)"


class ReleaseType(models.TextChoices):
    IMMEDIATE = "immediate", "Immediate"
    ON_DATE = "on_date", "On a specific date/time"
    AFTER_ENROLL_DAYS = "after_enroll_days", "After N days from enrollment"
    AFTER_LESSON_COMPLETE = "after_lesson_complete", "After another lesson is completed"


class VideoProvider(models.TextChoices):
    YOUTUBE = "youtube", "YouTube"
    VIMEO = "vimeo", "Vimeo"
    BUNNY = "bunny", "Bunny"
    CLOUDFLARE = "cloudflare", "Cloudflare Stream"
    S3 = "s3", "S3/Direct"
    OTHER = "other", "Other"


# ----------------------------- course modules/sections -----------------------------

class CourseModule(BranchScopedStampedOwnedActive):
    """
    A section/module inside a course.
    (Course metadata lives in courses.Course; this is the outline/content structure.)
    """

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="modules",
        db_index=True,
    )

    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True, null=True)

    visibility = models.CharField(
        max_length=20,
        choices=ModuleVisibility.choices,
        default=ModuleVisibility.PUBLIC,
        db_index=True,
    )

    sort_order = models.PositiveIntegerField(default=0, db_index=True)

    # optional: drip for whole module (rare; usually per lesson)
    release_type = models.CharField(
        max_length=30,
        choices=ReleaseType.choices,
        default=ReleaseType.IMMEDIATE,
        db_index=True,
    )
    release_at = models.DateTimeField(blank=True, null=True)
    release_after_days = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        db_table = "course_modules"
        ordering = ["sort_order", "created"]
        indexes = [
            models.Index(fields=["course", "sort_order"]),
            models.Index(fields=["branch", "active"]),
        ]

    def __str__(self):
        return f"{self.course_id} :: {self.title}"

    def save(self, *args, **kwargs):
        # keep branch consistent with course branch (prevents cross-branch content bugs)
        if self.course_id and self.branch_id is None:
            self.branch = self.course.branch
        super().save(*args, **kwargs)


# ----------------------------- lessons (content items) -----------------------------

class Lesson(BranchScopedStampedOwnedActive):
    """
    One table for all lesson types.
    Type-specific fields are optional.
    """

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="lessons",
        db_index=True,
    )
    module = models.ForeignKey(
        CourseModule,
        on_delete=models.CASCADE,
        related_name="lessons",
        db_index=True,
    )

    title = models.CharField(max_length=220, db_index=True)
    slug = models.SlugField(max_length=240, db_index=True)

    lesson_type = models.CharField(
        max_length=20,
        choices=LessonType.choices,
        default=LessonType.ARTICLE,
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=LessonStatus.choices,
        default=LessonStatus.DRAFT,
        db_index=True,
    )

    sort_order = models.PositiveIntegerField(default=0, db_index=True)

    # Short intro shown in outline
    summary = models.CharField(max_length=500, blank=True, null=True)

    # ---------- ARTICLE content ----------
    content_format = models.CharField(
        max_length=20,
        choices=ContentFormat.choices,
        default=ContentFormat.HTML,
    )
    body = models.TextField(blank=True, null=True)       # html/markdown
    body_blocks = models.JSONField(default=list, blank=True)  # blocks json (if using)

    # ---------- VIDEO content ----------
    video_provider = models.CharField(
        max_length=20,
        choices=VideoProvider.choices,
        blank=True,
        null=True,
        db_index=True,
    )
    video_url = models.URLField(blank=True, null=True)      # public link or signed link generator input
    video_asset_key = models.CharField(max_length=255, blank=True, null=True)  # storage id/stream id
    duration_seconds = models.PositiveIntegerField(default=0)

    # watch/completion rules
    require_watch_percent = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="0 means no watch requirement; 80 means must watch 80% to complete.",
    )

    # ---------- QUIZ/ASSIGNMENT linking ----------
    # These are string FKs so you can build those apps later without circular imports.
    quiz = models.ForeignKey(
        "assessments.Quiz",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="linked_lessons",
    )
    assignment = models.ForeignKey(
        "assessments.Assignment",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="linked_lessons",
    )

    # ---------- LIVE / EXTERNAL ----------
    external_url = models.URLField(blank=True, null=True)
    meeting_url = models.URLField(blank=True, null=True)
    starts_at = models.DateTimeField(blank=True, null=True)
    ends_at = models.DateTimeField(blank=True, null=True)

    # ---------- Access / release ----------
    is_preview = models.BooleanField(default=False, db_index=True)  # allow non-enrolled preview
    is_downloadable = models.BooleanField(default=False)            # for file lessons/resources

    release_type = models.CharField(
        max_length=30,
        choices=ReleaseType.choices,
        default=ReleaseType.IMMEDIATE,
        db_index=True,
    )
    release_at = models.DateTimeField(blank=True, null=True)
    release_after_days = models.PositiveIntegerField(blank=True, null=True)
    prerequisite_lesson = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="unlocks_lessons",
    )

    published_at = models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        db_table = "lessons"
        ordering = ["module__sort_order", "sort_order", "created"]
        constraints = [
            models.UniqueConstraint(fields=["course", "slug"], name="uniq_course_lesson_slug"),
        ]
        indexes = [
            models.Index(fields=["course", "module", "sort_order"]),
            models.Index(fields=["course", "status"]),
            models.Index(fields=["lesson_type"]),
            models.Index(fields=["release_type", "release_at"]),
            models.Index(fields=["branch", "active"]),
        ]

    def __str__(self):
        return f"{self.course_id} :: {self.title}"

    def save(self, *args, **kwargs):
        # keep branch consistent with course branch
        if self.course_id and self.branch_id is None:
            self.branch = self.course.branch
        super().save(*args, **kwargs)

    def publish(self):
        self.status = LessonStatus.PUBLISHED
        if not self.published_at:
            self.published_at = timezone.now()
        self.save(update_fields=["status", "published_at"])

    def is_released_for(self, enrolled_at: timezone.datetime | None, completed_lesson_ids: set[str] | None = None):
        """
        Pure helper. Your API/service can use this for gating.
        enrolled_at: datetime when the student enrolled.
        completed_lesson_ids: set of lesson ids completed.
        """
        now = timezone.now()
        if self.release_type == ReleaseType.IMMEDIATE:
            return True
        if self.release_type == ReleaseType.ON_DATE:
            return self.release_at is None or self.release_at <= now
        if self.release_type == ReleaseType.AFTER_ENROLL_DAYS:
            if not enrolled_at or self.release_after_days is None:
                return False
            return enrolled_at + timezone.timedelta(days=self.release_after_days) <= now
        if self.release_type == ReleaseType.AFTER_LESSON_COMPLETE:
            if not self.prerequisite_lesson_id:
                return True
            return bool(completed_lesson_ids and str(self.prerequisite_lesson_id) in completed_lesson_ids)
        return True


# ----------------------------- lesson resources/attachments -----------------------------

class ResourceType(models.TextChoices):
    FILE = "file", "File"
    LINK = "link", "Link"
    EMBED = "embed", "Embed"
    NOTE = "note", "Note"


class LessonResource(StampedOwnedActive):
    """
    Attachments/resources shown under a lesson: PDFs, ZIPs, links, etc.
    Store URL or storage_key depending on your storage strategy.
    """

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="resources", db_index=True)

    resource_type = models.CharField(max_length=10, choices=ResourceType.choices, default=ResourceType.FILE, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    # file storage fields
    file_url = models.URLField(blank=True, null=True)
    storage_key = models.CharField(max_length=255, blank=True, null=True)  # path/id in S3/Stream/etc.
    original_name = models.CharField(max_length=255, blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    size_bytes = models.BigIntegerField(blank=True, null=True)

    # link/embed
    link_url = models.URLField(blank=True, null=True)
    embed_code = models.TextField(blank=True, null=True)

    is_downloadable = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        db_table = "lesson_resources"
        ordering = ["sort_order", "created"]
        indexes = [
            models.Index(fields=["lesson", "sort_order"]),
        ]

    def __str__(self):
        return f"{self.lesson_id} :: {self.title}"


# ----------------------------- optional: content notes (teacher-only) -----------------------------

class LessonInstructorNote(StampedOwnedActive):
    """
    Internal notes for instructors/staff about this lesson.
    Students should never see this.
    """

    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="instructor_note")
    note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "lesson_instructor_notes"

    def __str__(self):
        return f"Note({self.lesson_id})"
