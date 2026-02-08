# certificates/models.py
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from core.utils.coreModels import StampedOwnedActive, BranchScopedStampedOwnedActive


# ----------------------------- choices -----------------------------

class TemplateStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    ARCHIVED = "archived", "Archived"


class IssueStatus(models.TextChoices):
    ISSUED = "issued", "Issued"
    REISSUED = "reissued", "Reissued"
    REVOKED = "revoked", "Revoked"


class PaperSize(models.TextChoices):
    A4 = "a4", "A4"
    LETTER = "letter", "Letter"


class Orientation(models.TextChoices):
    LANDSCAPE = "landscape", "Landscape"
    PORTRAIT = "portrait", "Portrait"


# ----------------------------- helpers -----------------------------

def make_verification_code() -> str:
    """
    Short-ish unique verification code (not guessable).
    UUID4 hex is fine for MVP.
    """
    return uuid.uuid4().hex


# ----------------------------- certificate template -----------------------------

class CertificateTemplate(BranchScopedStampedOwnedActive):
    """
    Template/design for a course certificate.
    Render strategy:
      - simplest: background image + dynamic text blocks (layout_json)
      - or HTML template (template_html) rendered to PDF
    """

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="certificate_templates",
        db_index=True,
    )

    name = models.CharField(max_length=180, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)

    status = models.CharField(max_length=20, choices=TemplateStatus.choices, default=TemplateStatus.DRAFT, db_index=True)

    paper_size = models.CharField(max_length=10, choices=PaperSize.choices, default=PaperSize.A4)
    orientation = models.CharField(max_length=12, choices=Orientation.choices, default=Orientation.LANDSCAPE)

    # Visual assets (store URLs or storage keys; keep it flexible)
    background_url = models.URLField(blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    signature_1_url = models.URLField(blank=True, null=True)
    signature_2_url = models.URLField(blank=True, null=True)

    # Content
    title_text = models.CharField(max_length=120, default="Certificate of Completion")
    subtitle_text = models.CharField(max_length=180, blank=True, null=True)

    # Option A: HTML template (render with your own engine later)
    template_html = models.TextField(blank=True, null=True)

    # Option B: JSON layout blocks (recommended MVP)
    # Example:
    # [{"type":"text","key":"student_name","x":120,"y":280,"fontSize":38,"fontWeight":"700"}, ...]
    layout_json = models.JSONField(default=list, blank=True)

    # Variables allowed: {{student_name}}, {{course_title}}, {{issue_date}}, {{certificate_no}}, {{verification_code}}
    allowed_variables = models.JSONField(
        default=list,
        blank=True,
        help_text="Optional: whitelist variables for editors",
    )

    is_default = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "certificate_templates"
        constraints = [
            models.UniqueConstraint(fields=["course", "slug"], name="uniq_course_certificate_template_slug"),
        ]
        indexes = [
            models.Index(fields=["course", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["is_default"]),
        ]

    def __str__(self):
        return f"{self.course_id} :: {self.name}"

    def save(self, *args, **kwargs):
        # keep branch consistent with course
        if self.course_id and self.branch_id is None:
            self.branch = self.course.branch
        super().save(*args, **kwargs)


# ----------------------------- eligibility rules -----------------------------

class CertificateRule(StampedOwnedActive):
    """
    Defines when a certificate can be issued for a course.
    One rule per course is enough for MVP.
    """

    course = models.OneToOneField(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="certificate_rule",
    )

    # Basic completion requirement
    require_course_completion = models.BooleanField(default=True)
    min_course_progress_percent = models.PositiveSmallIntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="100 means course must be fully completed.",
    )

    # Quiz requirement
    require_quiz_pass = models.BooleanField(default=False)
    quiz = models.ForeignKey(
        "assessments.Quiz",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="certificate_rules",
    )
    min_quiz_percent = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="0 disables score check; else requires >= this percent.",
    )

    # Assignment requirement
    require_assignment_pass = models.BooleanField(default=False)
    assignment = models.ForeignKey(
        "assessments.Assignment",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="certificate_rules",
    )
    min_assignment_marks = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="0 disables marks check; else requires >= this marks.",
    )

    # Extra knobs without migrations every time
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "certificate_rules"

    def __str__(self):
        return f"Rule({self.course_id})"


# ----------------------------- issued certificates -----------------------------

class CertificateIssue(BranchScopedStampedOwnedActive):
    """
    The issued certificate record.
    Typically one per user per course (but you can reissue and keep older ones revoked).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="certificates",
        db_index=True,
    )

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.PROTECT,
        related_name="issued_certificates",
        db_index=True,
    )

    enrollment = models.ForeignKey(
        "enrollments.Enrollment",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="certificates",
        db_index=True,
    )

    template = models.ForeignKey(
        CertificateTemplate,
        on_delete=models.PROTECT,
        related_name="issues",
        blank=True,
        null=True,
    )

    status = models.CharField(max_length=20, choices=IssueStatus.choices, default=IssueStatus.ISSUED, db_index=True)

    issued_at = models.DateTimeField(default=timezone.now, db_index=True)

    # human-readable number (optional: generate from settings.NumberSequence)
    certificate_no = models.CharField(max_length=60, blank=True, null=True, db_index=True)

    # public verification
    verification_code = models.CharField(max_length=64, unique=True, default=make_verification_code, db_index=True)

    # store generated file (pdf)
    pdf_url = models.URLField(blank=True, null=True)
    storage_key = models.CharField(max_length=255, blank=True, null=True)

    # snapshot fields (so certificate remains valid even if names change later)
    student_name = models.CharField(max_length=200, blank=True, null=True)
    course_title = models.CharField(max_length=220, blank=True, null=True)

    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="certificates_issued_by",
    )

    # revocation
    revoked_at = models.DateTimeField(blank=True, null=True)
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="certificates_revoked_by",
    )
    revoke_reason = models.TextField(blank=True, null=True)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "certificate_issues"
        indexes = [
            models.Index(fields=["course", "issued_at"]),
            models.Index(fields=["user", "issued_at"]),
            models.Index(fields=["branch", "issued_at"]),
            models.Index(fields=["status"]),
        ]
        constraints = [
            # one active issued certificate per user per course
            models.UniqueConstraint(
                fields=["user", "course"],
                condition=models.Q(status__in=[IssueStatus.ISSUED, IssueStatus.REISSUED]),
                name="uniq_active_certificate_user_course",
            )
        ]

    def __str__(self):
        return f"Certificate({self.user_id}::{self.course_id})"

    def save(self, *args, **kwargs):
        # keep branch consistent with course
        if self.course_id and self.branch_id is None:
            self.branch = self.course.branch

        # snapshot names if not already set
        if not self.student_name and self.user_id:
            # best-effort, works with your custom user
            try:
                self.student_name = getattr(self.user, "full_name", None) or f"{self.user}"
            except Exception:
                pass
        if not self.course_title and self.course_id:
            try:
                self.course_title = self.course.title
            except Exception:
                pass

        super().save(*args, **kwargs)

    def revoke(self, by_user=None, reason=None):
        self.status = IssueStatus.REVOKED
        self.revoked_at = timezone.now()
        self.revoked_by = by_user
        self.revoke_reason = reason
        self.save(update_fields=["status", "revoked_at", "revoked_by", "revoke_reason", "updated"])


# ----------------------------- events/audit -----------------------------

class CertificateEventType(models.TextChoices):
    ISSUED = "issued", "Issued"
    REISSUED = "reissued", "Reissued"
    REVOKED = "revoked", "Revoked"
    DOWNLOADED = "downloaded", "Downloaded"
    VERIFIED = "verified", "Verified"
    NOTE = "note", "Note"


class CertificateEvent(StampedOwnedActive):
    """
    Event log for certificate lifecycle and verification/audit.
    """

    certificate = models.ForeignKey(
        CertificateIssue,
        on_delete=models.CASCADE,
        related_name="events",
        db_index=True,
    )

    event_type = models.CharField(max_length=20, choices=CertificateEventType.choices, db_index=True)
    message = models.CharField(max_length=255, blank=True, null=True)
    data = models.JSONField(default=dict, blank=True)

    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "certificate_events"
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["certificate", "event_type"]),
            models.Index(fields=["event_type", "created"]),
        ]

    def __str__(self):
        return f"{self.certificate_id}::{self.event_type}"
