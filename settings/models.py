# settings/models.py
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from simple_history.models import HistoricalRecords

from core.utils.coreModels import UUIDPk, StampedOwnedActive


# ----------------------------- Reference Masters -----------------------------

class Currency(UUIDPk):
    code = models.CharField(max_length=3, unique=True, db_index=True)  # NPR, USD, AED
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10, blank=True, null=True)
    decimals = models.PositiveSmallIntegerField(default=2)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "currencies"

    def __str__(self):
        return self.code


class Country(UUIDPk):
    iso2 = models.CharField(max_length=2, unique=True, db_index=True)  # NP, AE
    name = models.CharField(max_length=80)
    phone_code = models.CharField(max_length=10, blank=True, null=True)  # +977
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "countries"

    def __str__(self):
        return self.name


class Language(UUIDPk):
    code = models.CharField(max_length=10, unique=True, db_index=True)  # en, ne
    name = models.CharField(max_length=50)
    is_rtl = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "languages"

    def __str__(self):
        return self.code


# ----------------------------- Organization / Branch -----------------------------

class OrganizationType(models.TextChoices):
    COACHING = "coaching", "Coaching/Institute"
    SCHOOL = "school", "School"
    COLLEGE = "college", "College"
    CORPORATE = "corporate", "Corporate Training"
    CREATOR = "creator", "Solo Creator"


class Organization(StampedOwnedActive):
    """
    Your tenant-ish root entity (even if you run single tenant now, this future-proofs you).
    """

    name = models.CharField(max_length=150, db_index=True)
    legal_name = models.CharField(max_length=200, blank=True, null=True)
    code = models.SlugField(max_length=60, unique=True, db_index=True)

    org_type = models.CharField(
        max_length=20, choices=OrganizationType.choices, default=OrganizationType.COACHING, db_index=True
    )

    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=True, null=True)
    city = models.CharField(max_length=80, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    timezone = models.CharField(max_length=64, default="Asia/Kathmandu")
    default_language = models.ForeignKey(Language, on_delete=models.PROTECT, blank=True, null=True)
    default_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, blank=True, null=True)

    logo_url = models.URLField(blank=True, null=True)

    history = HistoricalRecords(inherit=True)

    class Meta:
        db_table = "organizations"

    def __str__(self):
        return self.name


class BranchType(models.TextChoices):
    CAMPUS = "campus", "Campus"
    ONLINE = "online", "Online"
    HYBRID = "hybrid", "Hybrid"


class Branch(StampedOwnedActive):
    """
    Your branch-scoping target. Most of your models already reference Branch.
    """

    organization = models.ForeignKey(
        Organization, on_delete=models.PROTECT, related_name="branches", blank=True, null=True
    )

    name = models.CharField(max_length=150, db_index=True)
    code = models.SlugField(max_length=60, db_index=True)
    branch_type = models.CharField(max_length=10, choices=BranchType.choices, default=BranchType.CAMPUS)

    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)

    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=True, null=True)
    city = models.CharField(max_length=80, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    timezone = models.CharField(max_length=64, default="Asia/Kathmandu")
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, blank=True, null=True)

    is_default = models.BooleanField(default=False, db_index=True)

    history = HistoricalRecords(inherit=True)

    class Meta:
        db_table = "branches"
        constraints = [
            # Code should be unique inside an organization
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="uniq_branch_code_per_org",
            )
        ]
        indexes = [
            models.Index(fields=["organization", "active"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return f"{self.name}"


# ----------------------------- Settings Containers (JSON blobs) -----------------------------

class OrganizationSettings(StampedOwnedActive):
    """
    One blob to rule them all (simple and scalable).
    Put all org-level configuration here.
    """

    organization = models.OneToOneField(
        Organization, on_delete=models.CASCADE, related_name="settings"
    )

    # UI/branding
    branding = models.JSONField(default=dict, blank=True)  # {logo, colors, theme, etc}

    # system behavior
    general = models.JSONField(default=dict, blank=True)  # {timezone, language, etc}

    # auth/security
    security = models.JSONField(default=dict, blank=True)  # {otp, password_policy, session_ttl}

    # email/sms
    mail = models.JSONField(default=dict, blank=True)  # {provider, host, port, username}
    sms = models.JSONField(default=dict, blank=True)   # {provider, api_key}

    # storage + media protection (content leak controls)
    storage = models.JSONField(default=dict, blank=True)  # {s3, gcs, local}
    media_protection = models.JSONField(default=dict, blank=True)  # {watermark, signed_urls, download_block}

    # payment configs (even if billing app owns transactions)
    payments = models.JSONField(default=dict, blank=True)  # {khalti/esewa/stripe keys}

    history = HistoricalRecords(inherit=True)

    class Meta:
        db_table = "organization_settings"

    def __str__(self):
        return f"OrgSettings({self.organization_id})"


class BranchSettings(StampedOwnedActive):
    """
    Branch overrides (optional).
    Example: a branch uses different SMTP/SMS or different receipt headers.
    """

    branch = models.OneToOneField(Branch, on_delete=models.CASCADE, related_name="settings")
    data = models.JSONField(default=dict, blank=True)

    history = HistoricalRecords(inherit=True)

    class Meta:
        db_table = "branch_settings"

    def __str__(self):
        return f"BranchSettings({self.branch_id})"


# ----------------------------- Feature Flags -----------------------------

class FeatureScope(models.TextChoices):
    GLOBAL = "global", "Global"
    ORG = "org", "Organization"
    BRANCH = "branch", "Branch"


class FeatureFlag(StampedOwnedActive):
    key = models.SlugField(max_length=80, db_index=True)  # e.g. "enable_certificates"
    description = models.CharField(max_length=255, blank=True, null=True)
    enabled = models.BooleanField(default=False, db_index=True)

    scope = models.CharField(max_length=10, choices=FeatureScope.choices, default=FeatureScope.GLOBAL)

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, blank=True, null=True)

    history = HistoricalRecords(inherit=True)

    class Meta:
        db_table = "feature_flags"
        constraints = [
            models.UniqueConstraint(fields=["key", "scope", "organization", "branch"], name="uniq_feature_flag_scope")
        ]
        indexes = [
            models.Index(fields=["key", "enabled"]),
            models.Index(fields=["scope"]),
        ]

    def __str__(self):
        return f"{self.key} ({self.scope})"


# ----------------------------- Numbering / Sequences -----------------------------

class SequenceType(models.TextChoices):
    ENROLLMENT = "enrollment", "Enrollment"
    ORDER = "order", "Order"
    INVOICE = "invoice", "Invoice"
    RECEIPT = "receipt", "Receipt"
    CERTIFICATE = "certificate", "Certificate"
    TICKET = "ticket", "Support Ticket"


class NumberSequence(StampedOwnedActive):
    """
    If you want clean human-readable numbers:
    ENR-000001, INV-2026-000123, etc.
    """

    seq_type = models.CharField(max_length=20, choices=SequenceType.choices, db_index=True)

    # scope it to org/branch depending on your preference
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, blank=True, null=True)

    prefix = models.CharField(max_length=30, blank=True, null=True)  # e.g. "INV-2026-"
    padding = models.PositiveSmallIntegerField(default=6)            # 000001
    next_number = models.PositiveIntegerField(default=1)

    reset_yearly = models.BooleanField(default=False)
    last_reset_year = models.PositiveSmallIntegerField(blank=True, null=True)

    history = HistoricalRecords(inherit=True)

    class Meta:
        db_table = "number_sequences"
        constraints = [
            models.UniqueConstraint(
                fields=["seq_type", "organization", "branch"],
                name="uniq_sequence_scope",
            )
        ]

    def __str__(self):
        return f"{self.seq_type} seq"

    def maybe_reset(self):
        if not self.reset_yearly:
            return
        year = timezone.now().year
        if self.last_reset_year != year:
            self.next_number = 1
            self.last_reset_year = year
            self.save(update_fields=["next_number", "last_reset_year"])

    def peek(self):
        self.maybe_reset()
        number = str(self.next_number).zfill(self.padding)
        return f"{self.prefix or ''}{number}"

    def consume(self, save=True):
        value = self.peek()
        self.next_number += 1
        if save:
            self.save(update_fields=["next_number", "last_reset_year"])
        return value


# ----------------------------- Optional: Branch membership -----------------------------

class BranchMembership(StampedOwnedActive):
    """
    If a user can belong to multiple branches (common for staff/instructors).
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="branch_memberships")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="memberships")

    is_default = models.BooleanField(default=False, db_index=True)
    role_hint = models.CharField(max_length=50, blank=True, null=True)  # "admin", "instructor", etc.

    class Meta:
        db_table = "branch_memberships"
        constraints = [
            models.UniqueConstraint(fields=["user", "branch"], name="uniq_user_branch_membership")
        ]
        indexes = [
            models.Index(fields=["user", "is_default"]),
        ]

    def __str__(self):
        return f"{self.user_id} -> {self.branch_id}"
