# organizations/models.py
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.utils.coreModels import StampedOwnedActive


# ----------------------------- choices -----------------------------

class OrganizationType(models.TextChoices):
    COACHING = "coaching", "Coaching/Institute"
    SCHOOL = "school", "School"
    COLLEGE = "college", "College"
    CORPORATE = "corporate", "Corporate Training"
    CREATOR = "creator", "Solo Creator"


class MemberStatus(models.TextChoices):
    INVITED = "invited", "Invited"
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    LEFT = "left", "Left"


class InviteStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    EXPIRED = "expired", "Expired"
    REVOKED = "revoked", "Revoked"


# ----------------------------- core org -----------------------------

class Organization(StampedOwnedActive):
    """
    Root container for multi-institute support.
    Even if you start single-org, this future-proofs everything.
    """

    name = models.CharField(max_length=150, db_index=True)
    legal_name = models.CharField(max_length=200, blank=True, null=True)

    # short unique identifier (used in URLs/subdomains later)
    code = models.SlugField(max_length=60, unique=True, db_index=True)

    org_type = models.CharField(
        max_length=20,
        choices=OrganizationType.choices,
        default=OrganizationType.COACHING,
        db_index=True,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_organizations",
        blank=True,
        null=True,
    )

    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    country = models.CharField(max_length=80, blank=True, null=True)
    city = models.CharField(max_length=80, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    timezone = models.CharField(max_length=64, default="Asia/Kathmandu")
    default_language = models.CharField(max_length=10, default="en")  # keep simple
    default_currency = models.CharField(max_length=3, default="NPR")  # keep simple

    logo_url = models.URLField(blank=True, null=True)

    class Meta:
        db_table = "organizations"
        indexes = [
            models.Index(fields=["code", "active"]),
            models.Index(fields=["org_type", "active"]),
        ]

    def __str__(self):
        return self.name


# ----------------------------- org roles -----------------------------

class OrganizationRole(StampedOwnedActive):
    """
    Business roles inside an organization.
    Keep this separate from Django Groups (you can still map later).
    """

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="roles",
    )

    slug = models.SlugField(max_length=60, db_index=True)  # org_admin, instructor, support, etc.
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True, null=True)

    # simple permission bundle (you can evolve to fine-grained permissions later)
    permissions = models.JSONField(default=dict, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "organization_roles"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "slug"],
                name="uniq_org_role_slug",
            )
        ]

    def __str__(self):
        return f"{self.organization.code}:{self.slug}"


# ----------------------------- org membership -----------------------------

class OrganizationMember(StampedOwnedActive):
    """
    Membership of a user in an organization.

    NOTE:
    - Branch membership can live elsewhere (e.g., settings.BranchMembership).
    - This is the org-level access.
    """

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="organization_memberships",
    )

    role = models.ForeignKey(
        OrganizationRole,
        on_delete=models.PROTECT,
        related_name="members",
        blank=True,
        null=True,
    )

    status = models.CharField(max_length=20, choices=MemberStatus.choices, default=MemberStatus.ACTIVE, db_index=True)

    # optional convenience: default working branch (string ref prevents circular import)
    default_branch = models.ForeignKey(
        "settings.Branch",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="default_for_members",
    )

    joined_at = models.DateTimeField(blank=True, null=True)
    meta = models.JSONField(default=dict, blank=True)  # {"title":"", "department":""}

    class Meta:
        db_table = "organization_members"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user"],
                name="uniq_org_user",
            )
        ]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"{self.user_id} in {self.organization.code}"

    def activate(self):
        self.status = MemberStatus.ACTIVE
        if not self.joined_at:
            self.joined_at = timezone.now()
        self.save(update_fields=["status", "joined_at"])


# ----------------------------- org invites -----------------------------

class OrganizationInvite(StampedOwnedActive):
    """
    Invite users by email to join an organization.
    """

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="invites",
    )

    email = models.EmailField(db_index=True)

    role = models.ForeignKey(
        OrganizationRole,
        on_delete=models.PROTECT,
        related_name="invites",
        blank=True,
        null=True,
    )

    default_branch = models.ForeignKey(
        "settings.Branch",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="invites_default_branch",
    )

    token = models.CharField(max_length=128, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=InviteStatus.choices, default=InviteStatus.PENDING, db_index=True)

    expires_at = models.DateTimeField(db_index=True)
    accepted_at = models.DateTimeField(blank=True, null=True)

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sent_org_invites",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "organization_invites"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["email", "status"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"Invite({self.email} -> {self.organization.code})"

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    def mark_accepted(self):
        self.status = InviteStatus.ACCEPTED
        self.accepted_at = timezone.now()
        self.save(update_fields=["status", "accepted_at"])

    @staticmethod
    def default_expiry(days=7):
        return timezone.now() + timedelta(days=days)


# ----------------------------- optional: custom domains -----------------------------

class OrganizationDomain(StampedOwnedActive):
    """
    Optional: map custom domains/subdomains to an org (SaaS mode).
    """

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="domains",
    )

    domain = models.CharField(max_length=255, unique=True, db_index=True)  # example.com
    is_primary = models.BooleanField(default=False, db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    verified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "organization_domains"
        indexes = [
            models.Index(fields=["organization", "is_primary"]),
            models.Index(fields=["is_verified"]),
        ]

    def __str__(self):
        return f"{self.domain} -> {self.organization.code}"
