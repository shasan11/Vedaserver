# enrollments/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import Q

from core.utils.coreModels import StampedOwnedActive, BranchScopedStampedOwnedActive


# ----------------------------- choices -----------------------------

class EnrollmentStatus(models.TextChoices):
    PENDING = "pending", "Pending"          # created but not fully confirmed (payment/manual approval)
    ACTIVE = "active", "Active"             # student has access
    COMPLETED = "completed", "Completed"    # optional (usually derived from progress)
    EXPIRED = "expired", "Expired"          # access ended by time
    CANCELLED = "cancelled", "Cancelled"    # cancelled by admin/student
    REFUNDED = "refunded", "Refunded"       # paid enrollment refunded
    SUSPENDED = "suspended", "Suspended"    # blocked temporarily


class EnrollmentSource(models.TextChoices):
    SELF = "self", "Self"
    ADMIN = "admin", "Admin"
    PAYMENT = "payment", "Payment"
    IMPORT = "import", "Import"
    COUPON = "coupon", "Coupon"
    INVITE = "invite", "Invite"


class AccessType(models.TextChoices):
    LIFETIME = "lifetime", "Lifetime"
    TIME_LIMITED = "time_limited", "Time-limited"
    SUBSCRIPTION = "subscription", "Subscription"  # if you build plans later


class InviteStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    EXPIRED = "expired", "Expired"
    REVOKED = "revoked", "Revoked"


# ----------------------------- cohorts / batches (optional but real-world) -----------------------------

class CourseCohort(BranchScopedStampedOwnedActive):
    """
    Use this if you run batch-based / cohort classes.
    If your LMS is fully self-paced, you can skip this model entirely.
    """

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="cohorts",
        db_index=True,
    )

    name = models.CharField(max_length=150, db_index=True)  # e.g. "IELTS Feb 2026 Batch"
    code = models.SlugField(max_length=80, db_index=True)   # e.g. "ielts-feb-2026"

    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)
    enrollment_deadline = models.DateTimeField(blank=True, null=True)

    capacity = models.PositiveIntegerField(blank=True, null=True)
    is_open = models.BooleanField(default=True, db_index=True)
    is_default = models.BooleanField(default=False, db_index=True)

    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "course_cohorts"
        ordering = ["-start_at", "name"]
        constraints = [
            models.UniqueConstraint(fields=["course", "code"], name="uniq_course_cohort_code"),
        ]
        indexes = [
            models.Index(fields=["course", "is_open"]),
            models.Index(fields=["branch", "active"]),
        ]

    def __str__(self):
        return f"{self.course_id} :: {self.name}"

    def save(self, *args, **kwargs):
        # keep branch consistent with course
        if self.course_id and self.branch_id is None:
            self.branch = self.course.branch
        super().save(*args, **kwargs)


# ----------------------------- enrollment (core) -----------------------------

class Enrollment(BranchScopedStampedOwnedActive):
    """
    Grants a user access to a course (and optionally a cohort).
    This is THE gatekeeper for content access.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="enrollments",
        db_index=True,
    )

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.PROTECT,
        related_name="enrollments",
        db_index=True,
    )

    cohort = models.ForeignKey(
        CourseCohort,
        on_delete=models.PROTECT,
        related_name="enrollments",
        blank=True,
        null=True,
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.ACTIVE,
        db_index=True,
    )

    source = models.CharField(
        max_length=20,
        choices=EnrollmentSource.choices,
        default=EnrollmentSource.SELF,
        db_index=True,
    )

    access_type = models.CharField(
        max_length=20,
        choices=AccessType.choices,
        default=AccessType.LIFETIME,
        db_index=True,
    )

    enrolled_at = models.DateTimeField(default=timezone.now, db_index=True)
    access_starts_at = models.DateTimeField(blank=True, null=True)
    access_ends_at = models.DateTimeField(blank=True, null=True, db_index=True)

    # Payment linkage (keep flexible, so you can integrate billing later)
    billing_order_ref = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    currency_code = models.CharField(max_length=3, blank=True, null=True)
    price_paid = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    # admin actions / cancellation
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="enrollments_cancelled",
    )
    cancel_reason = models.TextField(blank=True, null=True)

    suspended_at = models.DateTimeField(blank=True, null=True)
    suspended_reason = models.TextField(blank=True, null=True)

    # free-form for weird cases (scholarship, corporate deal, etc.)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "enrollments"
        ordering = ["-enrolled_at"]
        indexes = [
            models.Index(fields=["course", "status"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["access_ends_at"]),
        ]
        constraints = [
            # One "ongoing" enrollment per user per course (prevents duplicates)
            models.UniqueConstraint(
                fields=["user", "course"],
                condition=Q(status__in=[
                    EnrollmentStatus.PENDING,
                    EnrollmentStatus.ACTIVE,
                    EnrollmentStatus.SUSPENDED,
                ]),
                name="uniq_ongoing_enrollment_user_course",
            )
        ]

    def __str__(self):
        return f"{self.user_id} -> {self.course_id} ({self.status})"

    def save(self, *args, **kwargs):
        # keep branch consistent with course
        if self.course_id and self.branch_id is None:
            self.branch = self.course.branch
        super().save(*args, **kwargs)

    @property
    def is_access_active(self) -> bool:
        """
        True if enrollment status + time window allows access.
        """
        if self.status not in (EnrollmentStatus.ACTIVE, EnrollmentStatus.COMPLETED):
            return False

        now = timezone.now()
        if self.access_starts_at and now < self.access_starts_at:
            return False
        if self.access_ends_at and now > self.access_ends_at:
            return False
        return True

    def expire_if_needed(self, save=True) -> bool:
        """
        Mark expired if time window ended.
        Returns True if changed.
        """
        if self.status in (EnrollmentStatus.CANCELLED, EnrollmentStatus.REFUNDED):
            return False
        if self.access_ends_at and timezone.now() > self.access_ends_at:
            self.status = EnrollmentStatus.EXPIRED
            if save:
                self.save(update_fields=["status"])
            return True
        return False

    def cancel(self, by_user=None, reason=None):
        self.status = EnrollmentStatus.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancelled_by = by_user
        self.cancel_reason = reason
        self.save(update_fields=["status", "cancelled_at", "cancelled_by", "cancel_reason"])

    def suspend(self, reason=None):
        self.status = EnrollmentStatus.SUSPENDED
        self.suspended_at = timezone.now()
        self.suspended_reason = reason
        self.save(update_fields=["status", "suspended_at", "suspended_reason"])


# ----------------------------- per-enrollment overrides -----------------------------

class EnrollmentAccessOverride(StampedOwnedActive):
    """
    Overrides to handle edge cases without hacking course/content logic.
    Example: allow downloads for a specific student, or extend access until date.
    """

    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="override",
    )

    # content permissions (optional)
    can_download_resources = models.BooleanField(default=False)
    can_view_even_if_unpublished = models.BooleanField(default=False)  # staff/tester like behavior
    can_access_certificate = models.BooleanField(default=True)

    # access window override
    override_access_ends_at = models.DateTimeField(blank=True, null=True)

    note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "enrollment_access_overrides"

    def __str__(self):
        return f"Override({self.enrollment_id})"


# ----------------------------- course access invites (private course flow) -----------------------------

class CourseAccessInvite(BranchScopedStampedOwnedActive):
    """
    Invite someone to enroll (email-based), useful for private/unlisted courses,
    corporate training, or admin-managed enrollments.
    """

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="access_invites",
        db_index=True,
    )

    cohort = models.ForeignKey(
        CourseCohort,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="access_invites",
    )

    email = models.EmailField(db_index=True)
    token = models.CharField(max_length=128, unique=True, db_index=True)

    status = models.CharField(
        max_length=20,
        choices=InviteStatus.choices,
        default=InviteStatus.PENDING,
        db_index=True,
    )

    expires_at = models.DateTimeField(db_index=True)
    accepted_at = models.DateTimeField(blank=True, null=True)

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="course_access_invites_sent",
    )

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "course_access_invites"
        indexes = [
            models.Index(fields=["course", "status"]),
            models.Index(fields=["email", "status"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"Invite({self.email} -> {self.course_id})"

    def save(self, *args, **kwargs):
        # keep branch consistent with course
        if self.course_id and self.branch_id is None:
            self.branch = self.course.branch
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    def mark_accepted(self):
        self.status = InviteStatus.ACCEPTED
        self.accepted_at = timezone.now()
        self.save(update_fields=["status", "accepted_at"])


# ----------------------------- enrollment events (audit trail) -----------------------------

class EnrollmentEventType(models.TextChoices):
    CREATED = "created", "Created"
    ACTIVATED = "activated", "Activated"
    CANCELLED = "cancelled", "Cancelled"
    REFUNDED = "refunded", "Refunded"
    SUSPENDED = "suspended", "Suspended"
    RESUMED = "resumed", "Resumed"
    EXPIRED = "expired", "Expired"
    EXTENDED = "extended", "Extended"
    NOTE = "note", "Note"


class EnrollmentEvent(StampedOwnedActive):
    """
    Event log so you can track what happened and why.
    This saves you from "why did this student lose access?" nightmares.
    """

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="events",
        db_index=True,
    )

    event_type = models.CharField(max_length=20, choices=EnrollmentEventType.choices, db_index=True)
    message = models.CharField(max_length=255, blank=True, null=True)
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "enrollment_events"
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["enrollment", "event_type"]),
        ]

    def __str__(self):
        return f"{self.enrollment_id}::{self.event_type}"
