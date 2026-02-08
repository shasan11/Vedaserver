# accounts/models.py
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


# ----------------------------- base mixins -----------------------------

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ----------------------------- user manager -----------------------------

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email).lower()
        extra_fields.setdefault("is_active", True)

        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email=email, password=password, **extra_fields)


# ----------------------------- core user -----------------------------

class UserType(models.TextChoices):
    STUDENT = "student", "Student"
    INSTRUCTOR = "instructor", "Instructor"
    STAFF = "staff", "Staff"  # internal ops staff (support/admin team)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Email-first auth user.
    Keep ONE user table for everyone, then attach role/profile models.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=30, blank=True, null=True, db_index=True)

    first_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80, blank=True)

    user_type = models.CharField(
        max_length=20, choices=UserType.choices, default=UserType.STUDENT, db_index=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # can access admin

    email_verified_at = models.DateTimeField(blank=True, null=True)
    phone_verified_at = models.DateTimeField(blank=True, null=True)

    last_seen_at = models.DateTimeField(blank=True, null=True)

    timezone = models.CharField(max_length=64, blank=True, default="Asia/Kathmandu")
    language = models.CharField(max_length=10, blank=True, default="en")

    # You can keep an image URL (CDN) instead of ImageField to avoid storage pain early
    avatar_url = models.URLField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return (f"{self.first_name} {self.last_name}").strip() or self.email

    def mark_seen(self):
        self.last_seen_at = timezone.now()
        self.save(update_fields=["last_seen_at"])


# ----------------------------- profiles -----------------------------

class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"
    NA = "na", "Prefer not to say"


class UserProfile(TimeStampedModel):
    """
    Common profile info for any user.
    Separate from User so User stays lean for auth + indexing.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.NA)
    dob = models.DateField(blank=True, null=True)

    country = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    bio = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    class Meta:
        db_table = "user_profiles"

    def __str__(self):
        return f"Profile({self.user_id})"


class StudentProfile(TimeStampedModel):
    """
    Student-specific fields.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )

    guardian_name = models.CharField(max_length=150, blank=True, null=True)
    guardian_phone = models.CharField(max_length=30, blank=True, null=True)

    # optional segmentation
    level = models.CharField(max_length=80, blank=True, null=True)  # e.g. "Class 12", "Bachelor", etc.
    institute = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        db_table = "student_profiles"

    def __str__(self):
        return f"StudentProfile({self.user_id})"


class InstructorProfile(TimeStampedModel):
    """
    Instructor-specific fields.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instructor_profile",
    )

    headline = models.CharField(max_length=200, blank=True, null=True)  # e.g. "IELTS Mentor | 8+ years"
    about = models.TextField(blank=True, null=True)

    # keep simple now; later you can normalize into Skill model
    expertise = models.JSONField(default=list, blank=True)  # ["IELTS", "Physics", "React"]

    is_verified = models.BooleanField(default=False, db_index=True)
    verified_at = models.DateTimeField(blank=True, null=True)

    # payouts (if you plan instructor revenue sharing)
    payout_method = models.CharField(max_length=40, blank=True, null=True)  # "bank", "khalti", "stripe"
    payout_details = models.JSONField(default=dict, blank=True)  # {"account_no": "..."} etc

    class Meta:
        db_table = "instructor_profiles"

    def __str__(self):
        return f"InstructorProfile({self.user_id})"


# ----------------------------- roles (optional, but useful) -----------------------------

class Role(TimeStampedModel):
    """
    Lightweight business roles (different from Django groups if you want both).
    Example: owner, org_admin, content_manager, instructor, student, support_agent.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    slug = models.SlugField(unique=True, db_index=True)   # "student", "instructor", "support"
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True, null=True)

    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "roles"

    def __str__(self):
        return self.name


class UserRole(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_users")

    class Meta:
        db_table = "user_roles"
        constraints = [
            models.UniqueConstraint(fields=["user", "role"], name="uniq_user_role")
        ]

    def __str__(self):
        return f"{self.user_id} -> {self.role.slug}"


# ----------------------------- verification / tokens -----------------------------

class TokenPurpose(models.TextChoices):
    VERIFY_EMAIL = "verify_email", "Verify Email"
    RESET_PASSWORD = "reset_password", "Reset Password"
    LOGIN_OTP = "login_otp", "Login OTP"


class UserToken(TimeStampedModel):
    """
    A single table for verification links + password resets + OTPs.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tokens",
    )

    purpose = models.CharField(max_length=30, choices=TokenPurpose.choices, db_index=True)

    token = models.CharField(max_length=128, unique=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)

    used_at = models.DateTimeField(blank=True, null=True)
    sent_to = models.CharField(max_length=255, blank=True, null=True)  # email or phone
    meta = models.JSONField(default=dict, blank=True)  # {"ip": "...", "ua": "..."} etc

    class Meta:
        db_table = "user_tokens"
        indexes = [
            models.Index(fields=["user", "purpose", "expires_at"]),
        ]

    def __str__(self):
        return f"{self.purpose}:{self.user_id}"

    @property
    def is_used(self):
        return self.used_at is not None

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    def mark_used(self):
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])

    @staticmethod
    def default_expiry(minutes=30):
        return timezone.now() + timedelta(minutes=minutes)


# ----------------------------- audit -----------------------------

class LoginAudit(TimeStampedModel):
    """
    Helps you debug login issues + detect abuse.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="login_audits",
    )

    email_entered = models.EmailField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    success = models.BooleanField(default=False, db_index=True)
    failure_reason = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "login_audits"
        indexes = [
            models.Index(fields=["created_at", "success"]),
            models.Index(fields=["ip_address", "created_at"]),
        ]

    def __str__(self):
        return f"LoginAudit({self.email_entered}, success={self.success})"
