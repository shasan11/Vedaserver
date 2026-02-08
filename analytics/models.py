# analytics/models.py
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from core.utils.coreModels import UUIDPk, StampedOwnedActive


# ----------------------------- lean bases (NO history) -----------------------------

class AnalyticsStamped(UUIDPk):
    """
    Lean base for high-write analytics tables.
    No simple_history, no user_add, minimal overhead.
    """
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BranchBound(models.Model):
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

class DeviceType(models.TextChoices):
    DESKTOP = "desktop", "Desktop"
    MOBILE = "mobile", "Mobile"
    TABLET = "tablet", "Tablet"
    BOT = "bot", "Bot"
    OTHER = "other", "Other"


class SessionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    ENDED = "ended", "Ended"


class EventType(models.TextChoices):
    # general
    PAGE_VIEW = "page_view", "Page view"
    CLICK = "click", "Click"
    SEARCH = "search", "Search"
    LOGIN = "login", "Login"
    LOGOUT = "logout", "Logout"

    # course funnel
    COURSE_VIEW = "course_view", "Course viewed"
    ADD_TO_CART = "add_to_cart", "Added to cart"
    CHECKOUT_STARTED = "checkout_started", "Checkout started"
    PAYMENT_INITIATED = "payment_initiated", "Payment initiated"
    PAYMENT_SUCCESS = "payment_success", "Payment success"
    PAYMENT_FAILED = "payment_failed", "Payment failed"
    ENROLLED = "enrolled", "Enrolled"

    # learning
    MODULE_VIEW = "module_view", "Module viewed"
    LESSON_START = "lesson_start", "Lesson started"
    LESSON_PROGRESS = "lesson_progress", "Lesson progress ping"
    LESSON_COMPLETE = "lesson_complete", "Lesson completed"

    # assessments
    QUIZ_START = "quiz_start", "Quiz started"
    QUIZ_SUBMIT = "quiz_submit", "Quiz submitted"
    QUIZ_PASS = "quiz_pass", "Quiz passed"
    QUIZ_FAIL = "quiz_fail", "Quiz failed"

    ASSIGNMENT_SUBMIT = "assignment_submit", "Assignment submitted"
    ASSIGNMENT_GRADED = "assignment_graded", "Assignment graded"

    # reviews/certs
    REVIEW_CREATED = "review_created", "Review created"
    CERT_ISSUED = "cert_issued", "Certificate issued"


class MetricName(models.TextChoices):
    # Global KPIs
    ACTIVE_USERS = "active_users", "Active Users"
    NEW_USERS = "new_users", "New Users"
    SESSIONS = "sessions", "Sessions"
    PAGE_VIEWS = "page_views", "Page Views"

    # Funnel KPIs
    COURSE_VIEWS = "course_views", "Course Views"
    CHECKOUTS = "checkouts", "Checkouts Started"
    ORDERS_PAID = "orders_paid", "Orders Paid"
    REVENUE = "revenue", "Revenue"

    # Learning KPIs
    LESSON_STARTS = "lesson_starts", "Lesson Starts"
    LESSON_COMPLETIONS = "lesson_completions", "Lesson Completions"
    WATCH_TIME_SECONDS = "watch_time_seconds", "Watch Time (Seconds)"


# ----------------------------- acquisition / campaigns -----------------------------

class AcquisitionCampaign(StampedOwnedActive):
    """
    Low volume table. OK to use your normal base.
    Used for tracking UTM/campaign metadata and matching on events.
    """

    name = models.CharField(max_length=160, db_index=True)
    source = models.CharField(max_length=80, blank=True, null=True, db_index=True)   # utm_source
    medium = models.CharField(max_length=80, blank=True, null=True, db_index=True)   # utm_medium
    campaign = models.CharField(max_length=120, blank=True, null=True, db_index=True)  # utm_campaign
    content = models.CharField(max_length=120, blank=True, null=True)                # utm_content
    term = models.CharField(max_length=120, blank=True, null=True)                   # utm_term

    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "acquisition_campaigns"
        indexes = [
            models.Index(fields=["source", "medium"]),
            models.Index(fields=["campaign"]),
        ]

    def __str__(self):
        return self.name


# ----------------------------- sessions -----------------------------

class AnalyticsSession(AnalyticsStamped, BranchBound):
    """
    One session = browsing window (anonymous or logged-in).
    """

    session_key = models.CharField(max_length=80, db_index=True)  # your frontend can generate UUID for this
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="analytics_sessions",
        db_index=True,
    )

    status = models.CharField(max_length=10, choices=SessionStatus.choices, default=SessionStatus.ACTIVE, db_index=True)

    started_at = models.DateTimeField(default=timezone.now, db_index=True)
    last_seen_at = models.DateTimeField(default=timezone.now, db_index=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    device_type = models.CharField(max_length=10, choices=DeviceType.choices, default=DeviceType.OTHER, db_index=True)
    device_os = models.CharField(max_length=60, blank=True, null=True)
    browser = models.CharField(max_length=60, blank=True, null=True)

    referrer = models.URLField(blank=True, null=True)
    landing_path = models.CharField(max_length=255, blank=True, null=True)

    # UTM
    utm_source = models.CharField(max_length=80, blank=True, null=True, db_index=True)
    utm_medium = models.CharField(max_length=80, blank=True, null=True, db_index=True)
    utm_campaign = models.CharField(max_length=120, blank=True, null=True, db_index=True)
    utm_content = models.CharField(max_length=120, blank=True, null=True)
    utm_term = models.CharField(max_length=120, blank=True, null=True)

    campaign_obj = models.ForeignKey(
        AcquisitionCampaign,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sessions",
    )

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "analytics_sessions"
        indexes = [
            models.Index(fields=["branch", "started_at"]),
            models.Index(fields=["user", "started_at"]),
            models.Index(fields=["status", "last_seen_at"]),
        ]

    def __str__(self):
        return f"Session({self.session_key})"


# ----------------------------- events -----------------------------

class AnalyticsEvent(AnalyticsStamped, BranchBound):
    """
    Event stream. Keep it lean.
    If you log LESSON_PROGRESS pings every 5 seconds for every student,
    this table will explode — so throttle it (10–30s) or aggregate client-side.
    """

    session = models.ForeignKey(
        AnalyticsSession,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="events",
        db_index=True,
    )

    occurred_at = models.DateTimeField(default=timezone.now, db_index=True)

    event_type = models.CharField(max_length=40, choices=EventType.choices, db_index=True)
    name = models.CharField(max_length=120, blank=True, null=True, db_index=True)  # optional custom name

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="analytics_events",
        db_index=True,
    )

    # Common navigation fields (good for page views)
    path = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    page_title = models.CharField(max_length=200, blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)

    # Common product objects (fast filtering without generic joins)
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="analytics_events",
        db_index=True,
    )
    lesson = models.ForeignKey(
        "content.Lesson",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="analytics_events",
        db_index=True,
    )
    enrollment = models.ForeignKey(
        "enrollments.Enrollment",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="analytics_events",
        db_index=True,
    )
    order = models.ForeignKey(
        "billing.Order",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="analytics_events",
        db_index=True,
    )

    # Optional generic target (if you want to attach event to ANY model)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, blank=True, null=True)
    object_id = models.CharField(max_length=64, blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    # Numbers (useful for progress/watch time/amounts)
    value = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(default=0)

    # Extra stuff (search query, button id, error payload, etc.)
    properties = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "analytics_events"
        indexes = [
            models.Index(fields=["branch", "occurred_at"]),
            models.Index(fields=["event_type", "occurred_at"]),
            models.Index(fields=["user", "occurred_at"]),
            models.Index(fields=["course", "occurred_at"]),
            models.Index(fields=["lesson", "occurred_at"]),
            models.Index(fields=["path", "occurred_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} @ {self.occurred_at}"

    def save(self, *args, **kwargs):
        # best-effort branch propagation
        if self.branch_id is None:
            if self.course_id and getattr(self.course, "branch_id", None):
                self.branch_id = self.course.branch_id
            elif self.lesson_id and getattr(self.lesson, "branch_id", None):
                self.branch_id = self.lesson.branch_id
            elif self.session_id and getattr(self.session, "branch_id", None):
                self.branch_id = self.session.branch_id
        super().save(*args, **kwargs)


# ----------------------------- daily aggregates (fast dashboards) -----------------------------

class DailyMetric(AnalyticsStamped, BranchBound):
    """
    Pre-aggregated numbers per day.
    Your cron/celery job updates these from AnalyticsEvent.
    """

    date = models.DateField(db_index=True)
    metric = models.CharField(max_length=40, choices=MetricName.choices, db_index=True)

    value = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    # optional breakdown dimensions
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="daily_metrics",
        db_index=True,
    )
    campaign = models.ForeignKey(
        AcquisitionCampaign,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="daily_metrics",
        db_index=True,
    )

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "daily_metrics"
        constraints = [
            models.UniqueConstraint(
                fields=["branch", "date", "metric", "course", "campaign"],
                name="uniq_daily_metric_branch_date_metric_dims",
            )
        ]
        indexes = [
            models.Index(fields=["branch", "date"]),
            models.Index(fields=["metric", "date"]),
            models.Index(fields=["course", "date"]),
        ]

    def __str__(self):
        return f"{self.date} {self.metric}={self.value}"


# ----------------------------- cohorts / retention snapshots -----------------------------

class CohortType(models.TextChoices):
    SIGNUP = "signup", "Signup cohort"
    ENROLLMENT = "enrollment", "Enrollment cohort"


class RetentionCohort(StampedOwnedActive):
    """
    Low volume summary table. OK to use normal base.
    Stores retention numbers like day_0/day_1/day_7/day_30 etc.
    """

    branch = models.ForeignKey("settings.Branch", on_delete=models.PROTECT, related_name="retention_cohorts", db_index=True)

    cohort_type = models.CharField(max_length=20, choices=CohortType.choices, default=CohortType.SIGNUP, db_index=True)

    cohort_date = models.DateField(db_index=True)  # the cohort start day
    course = models.ForeignKey("courses.Course", on_delete=models.SET_NULL, blank=True, null=True, related_name="retention_cohorts", db_index=True)

    size = models.PositiveIntegerField(default=0)

    # Example: {"d1": 120, "d7": 60, "d30": 12}
    retention = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "retention_cohorts"
        constraints = [
            models.UniqueConstraint(fields=["branch", "cohort_type", "cohort_date", "course"], name="uniq_retention_cohort_dims")
        ]
        indexes = [
            models.Index(fields=["branch", "cohort_date"]),
            models.Index(fields=["cohort_type", "cohort_date"]),
        ]

    def __str__(self):
        return f"{self.branch_id} {self.cohort_type} {self.cohort_date}"
