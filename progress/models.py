# progress/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from core.utils.coreModels import UUIDPk


# ----------------------------- lean base (NO history) -----------------------------

class ProgressStamped(UUIDPk):
    """
    Lean base for high-write tables (progress updates, pings, video offsets).
    DO NOT add simple_history here, it will explode storage.
    """
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BranchBound(models.Model):
    """
    Keep branch denormalized for fast filtering.
    Always set it from course.branch / lesson.branch.
    """
    branch = models.ForeignKey(
        "settings.Branch",
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_branch",
        blank=True,
        null=True,
        db_index=True,
    )

    class Meta:
        abstract = True


# ----------------------------- choices -----------------------------

class CourseProgressStatus(models.TextChoices):
    NOT_STARTED = "not_started", "Not started"
    IN_PROGRESS = "in_progress", "In progress"
    COMPLETED = "completed", "Completed"


class LessonProgressStatus(models.TextChoices):
    NOT_STARTED = "not_started", "Not started"
    IN_PROGRESS = "in_progress", "In progress"
    COMPLETED = "completed", "Completed"


class ProgressSource(models.TextChoices):
    WEB = "web", "Web"
    MOBILE = "mobile", "Mobile"
    API = "api", "API"


# ----------------------------- course progress -----------------------------

class CourseProgress(ProgressStamped, BranchBound):
    """
    One record per user per course.
    Denormalized counters make dashboards fast.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_progress",
        db_index=True,
    )

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="progress_records",
        db_index=True,
    )

    # optional: tie to current enrollment for access windows / paid vs free
    enrollment = models.ForeignKey(
        "enrollments.Enrollment",
        on_delete=models.SET_NULL,
        related_name="progress_records",
        blank=True,
        null=True,
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=CourseProgressStatus.choices,
        default=CourseProgressStatus.NOT_STARTED,
        db_index=True,
    )

    started_at = models.DateTimeField(blank=True, null=True, db_index=True)
    completed_at = models.DateTimeField(blank=True, null=True, db_index=True)
    last_activity_at = models.DateTimeField(blank=True, null=True, db_index=True)

    # denormalized counts (keep updated from services/signals)
    total_lessons = models.PositiveIntegerField(default=0)
    completed_lessons = models.PositiveIntegerField(default=0)

    progress_percent = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        db_index=True,
    )

    # last visited
    last_lesson = models.ForeignKey(
        "content.Lesson",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="last_for_course_progress",
    )

    # aggregated watch/reading time (optional)
    total_time_spent_seconds = models.PositiveIntegerField(default=0)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "course_progress"
        constraints = [
            models.UniqueConstraint(fields=["user", "course"], name="uniq_user_course_progress"),
        ]
        indexes = [
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["course", "status"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["progress_percent"]),
        ]

    def __str__(self):
        return f"{self.user_id} :: {self.course_id} :: {self.status}"

    def touch(self):
        now = timezone.now()
        if not self.started_at:
            self.started_at = now
            self.status = CourseProgressStatus.IN_PROGRESS
        self.last_activity_at = now
        self.save(update_fields=["started_at", "status", "last_activity_at", "updated"])

    def mark_completed(self):
        now = timezone.now()
        self.status = CourseProgressStatus.COMPLETED
        if not self.completed_at:
            self.completed_at = now
        self.last_activity_at = now
        self.progress_percent = 100
        self.save(update_fields=["status", "completed_at", "last_activity_at", "progress_percent", "updated"])


# ----------------------------- lesson progress -----------------------------

class LessonProgress(ProgressStamped, BranchBound):
    """
    One record per user per lesson.
    Used for gating drip-release (prerequisite lesson completed).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_progress",
        db_index=True,
    )

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="lesson_progress_records",
        db_index=True,
    )

    lesson = models.ForeignKey(
        "content.Lesson",
        on_delete=models.CASCADE,
        related_name="progress_records",
        db_index=True,
    )

    enrollment = models.ForeignKey(
        "enrollments.Enrollment",
        on_delete=models.SET_NULL,
        related_name="lesson_progress_records",
        blank=True,
        null=True,
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=LessonProgressStatus.choices,
        default=LessonProgressStatus.NOT_STARTED,
        db_index=True,
    )

    started_at = models.DateTimeField(blank=True, null=True, db_index=True)
    completed_at = models.DateTimeField(blank=True, null=True, db_index=True)
    last_accessed_at = models.DateTimeField(blank=True, null=True, db_index=True)

    # general progress (article/file/etc.)
    progress_percent = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        db_index=True,
    )

    # video tracking (safe defaults for other types)
    last_position_seconds = models.PositiveIntegerField(default=0)
    watched_seconds = models.PositiveIntegerField(default=0)

    # for “resume” UX (articles / blocks)
    last_scroll_percent = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    # optional: completion confirmation by instructor/staff (for assignments/live sessions)
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="lesson_progress_completed_by",
    )

    completion_note = models.TextField(blank=True, null=True)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "lesson_progress"
        constraints = [
            models.UniqueConstraint(fields=["user", "lesson"], name="uniq_user_lesson_progress"),
        ]
        indexes = [
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["course", "status"]),
            models.Index(fields=["lesson", "status"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"{self.user_id} :: {self.lesson_id} :: {self.status}"

    def start(self, source=ProgressSource.WEB):
        now = timezone.now()
        if not self.started_at:
            self.started_at = now
        self.status = LessonProgressStatus.IN_PROGRESS
        self.last_accessed_at = now
        self.meta.setdefault("source", source)
        self.save(update_fields=["started_at", "status", "last_accessed_at", "meta", "updated"])

    def update_video_ping(self, position_seconds: int, watched_increment_seconds: int = 0):
        """
        Call this from your /ping endpoint (every 10-30s).
        Keep it simple: update counters, don’t create rows.
        """
        now = timezone.now()
        self.last_accessed_at = now
        self.last_position_seconds = max(0, int(position_seconds))
        if watched_increment_seconds:
            self.watched_seconds += max(0, int(watched_increment_seconds))
        self.status = self.status if self.status != LessonProgressStatus.NOT_STARTED else LessonProgressStatus.IN_PROGRESS
        self.save(update_fields=["last_accessed_at", "last_position_seconds", "watched_seconds", "status", "updated"])

    def mark_completed(self, by_user=None, note=None):
        now = timezone.now()
        self.status = LessonProgressStatus.COMPLETED
        if not self.started_at:
            self.started_at = now
        self.completed_at = now
        self.last_accessed_at = now
        self.progress_percent = 100
        if by_user:
            self.completed_by = by_user
        if note:
            self.completion_note = note
        self.save(update_fields=[
            "status", "started_at", "completed_at", "last_accessed_at",
            "progress_percent", "completed_by", "completion_note", "updated"
        ])


# ----------------------------- daily time aggregates (analytics-friendly) -----------------------------

class DailyLearningTime(ProgressStamped, BranchBound):
    """
    Lightweight aggregate: per user per day time spent.
    Great for dashboards without event spam.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_learning_time",
        db_index=True,
    )

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.SET_NULL,
        related_name="daily_learning_time",
        blank=True,
        null=True,
        db_index=True,
    )

    date = models.DateField(db_index=True)
    seconds = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "daily_learning_time"
        constraints = [
            models.UniqueConstraint(fields=["user", "course", "date"], name="uniq_user_course_date"),
        ]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["user", "date"]),
            models.Index(fields=["course", "date"]),
            models.Index(fields=["branch", "date"]),
        ]

    def __str__(self):
        return f"{self.user_id} {self.date} {self.seconds}s"


# ----------------------------- optional: progress events (if you want audit) -----------------------------

class ProgressEventType(models.TextChoices):
    LESSON_STARTED = "lesson_started", "Lesson started"
    LESSON_PING = "lesson_ping", "Lesson ping"
    LESSON_COMPLETED = "lesson_completed", "Lesson completed"
    COURSE_COMPLETED = "course_completed", "Course completed"


class ProgressEvent(ProgressStamped, BranchBound):
    """
    Optional. Use only if you truly need event-level audit/analytics.
    If you log every ping here, DB will grow fast.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progress_events", db_index=True)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="progress_events", db_index=True)
    lesson = models.ForeignKey("content.Lesson", on_delete=models.SET_NULL, blank=True, null=True, related_name="progress_events")

    event_type = models.CharField(max_length=30, choices=ProgressEventType.choices, db_index=True)
    source = models.CharField(max_length=10, choices=ProgressSource.choices, default=ProgressSource.WEB)

    data = models.JSONField(default=dict, blank=True)  # {"pos": 120, "watched_inc": 10} etc.

    class Meta:
        db_table = "progress_events"
        indexes = [
            models.Index(fields=["user", "created"]),
            models.Index(fields=["course", "created"]),
            models.Index(fields=["event_type", "created"]),
        ]

    def __str__(self):
        return f"{self.user_id} :: {self.event_type}"
