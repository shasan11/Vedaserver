# communication/models.py
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from core.utils.coreModels import StampedOwnedActive, BranchScopedStampedOwnedActive, UUIDPk


# ----------------------------- lean base for high-volume tables -----------------------------

class CommStamped(UUIDPk):
    """
    Lean base for high-volume tables (notifications/outbound queue).
    NO history, no user_add, minimal indexes.
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


# ----------------------------- templates -----------------------------

class TemplateChannel(models.TextChoices):
    IN_APP = "in_app", "In-app"
    EMAIL = "email", "Email"
    SMS = "sms", "SMS"
    PUSH = "push", "Push"


class MessageTemplate(BranchScopedStampedOwnedActive):
    """
    Reusable templates for notifications/emails/SMS.
    Use {{var}} placeholders; render in service layer.
    """

    key = models.SlugField(max_length=80, db_index=True)  # e.g. "enrollment_created"
    name = models.CharField(max_length=120)
    channel = models.CharField(max_length=10, choices=TemplateChannel.choices, db_index=True)

    subject = models.CharField(max_length=200, blank=True, null=True)  # mainly for email
    body = models.TextField()  # in-app/email/sms body

    # optional: store variables schema
    variables = models.JSONField(default=list, blank=True)  # ["student_name","course_title"]

    class Meta:
        db_table = "message_templates"
        constraints = [
            models.UniqueConstraint(fields=["branch", "key", "channel"], name="uniq_template_branch_key_channel")
        ]
        indexes = [
            models.Index(fields=["key", "channel"]),
            models.Index(fields=["branch", "active"]),
        ]

    def __str__(self):
        return f"{self.key} ({self.channel})"


# ----------------------------- announcements -----------------------------

class AudienceType(models.TextChoices):
    ALL_BRANCH = "all_branch", "All users in branch"
    COURSE_ENROLLED = "course_enrolled", "Enrolled in a course"
    ROLE = "role", "Specific role"
    USERS = "users", "Specific users"


class AnnouncementStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class Announcement(BranchScopedStampedOwnedActive):
    """
    Broadcast messages (banner, notice board, etc.)
    """

    title = models.CharField(max_length=200, db_index=True)
    body = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=AnnouncementStatus.choices, default=AnnouncementStatus.DRAFT, db_index=True)

    audience_type = models.CharField(max_length=20, choices=AudienceType.choices, default=AudienceType.ALL_BRANCH, db_index=True)

    # audience filters
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="announcements",
    )
    role_slug = models.CharField(max_length=60, blank=True, null=True)  # e.g. "instructor", "student"

    # visibility window
    publish_at = models.DateTimeField(blank=True, null=True, db_index=True)
    expire_at = models.DateTimeField(blank=True, null=True, db_index=True)

    is_pinned = models.BooleanField(default=False, db_index=True)
    priority = models.PositiveSmallIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)], db_index=True)

    action_url = models.URLField(blank=True, null=True)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "announcements"
        indexes = [
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["status", "publish_at"]),
            models.Index(fields=["is_pinned", "priority"]),
        ]

    def __str__(self):
        return self.title

    def is_live(self):
        now = timezone.now()
        if self.status != AnnouncementStatus.PUBLISHED:
            return False
        if self.publish_at and now < self.publish_at:
            return False
        if self.expire_at and now > self.expire_at:
            return False
        return True


class AnnouncementTargetUser(StampedOwnedActive):
    """
    Only used when audience_type = USERS
    """
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name="target_users", db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="targeted_announcements", db_index=True)

    class Meta:
        db_table = "announcement_target_users"
        constraints = [
            models.UniqueConstraint(fields=["announcement", "user"], name="uniq_announcement_target_user")
        ]


# ----------------------------- in-app notifications -----------------------------

class NotificationPriority(models.TextChoices):
    LOW = "low", "Low"
    NORMAL = "normal", "Normal"
    HIGH = "high", "High"
    URGENT = "urgent", "Urgent"


class NotificationStatus(models.TextChoices):
    CREATED = "created", "Created"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"


class Notification(CommStamped, BranchBound):
    """
    In-app notification (bell icon).
    High volume → lean model.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        db_index=True,
    )

    title = models.CharField(max_length=200)
    body = models.TextField(blank=True, null=True)

    priority = models.CharField(max_length=10, choices=NotificationPriority.choices, default=NotificationPriority.NORMAL, db_index=True)

    status = models.CharField(max_length=20, choices=NotificationStatus.choices, default=NotificationStatus.CREATED, db_index=True)

    # link for UI navigation
    action_url = models.URLField(blank=True, null=True)

    # optional generic link to any object: Order, Enrollment, CertificateIssue, etc.
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, blank=True, null=True)
    object_id = models.CharField(max_length=64, blank=True, null=True)  # UUID string
    content_object = GenericForeignKey("content_type", "object_id")

    data = models.JSONField(default=dict, blank=True)

    read_at = models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        db_table = "notifications"
        indexes = [
            models.Index(fields=["user", "read_at"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["branch", "created"]),
        ]

    def __str__(self):
        return f"Notif({self.user_id})"

    @property
    def is_read(self):
        return self.read_at is not None

    def mark_read(self):
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=["read_at", "updated"])


# ----------------------------- outbound queue (email/sms/push) -----------------------------

class OutboundChannel(models.TextChoices):
    EMAIL = "email", "Email"
    SMS = "sms", "SMS"
    PUSH = "push", "Push"


class OutboundStatus(models.TextChoices):
    QUEUED = "queued", "Queued"
    PROCESSING = "processing", "Processing"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class OutboundMessage(CommStamped, BranchBound):
    """
    Queue table for email/sms/push. Send with Celery/cron.
    Keep payload snapshot + provider response.
    """

    channel = models.CharField(max_length=10, choices=OutboundChannel.choices, db_index=True)
    status = models.CharField(max_length=20, choices=OutboundStatus.choices, default=OutboundStatus.QUEUED, db_index=True)

    # who it’s for (optional)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="outbound_messages",
        db_index=True,
    )

    to = models.CharField(max_length=255, db_index=True)  # email or phone or device token
    subject = models.CharField(max_length=200, blank=True, null=True)
    body = models.TextField()

    template_key = models.SlugField(max_length=80, blank=True, null=True, db_index=True)
    variables = models.JSONField(default=dict, blank=True)

    scheduled_at = models.DateTimeField(blank=True, null=True, db_index=True)
    sent_at = models.DateTimeField(blank=True, null=True, db_index=True)

    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=3)

    provider = models.CharField(max_length=40, blank=True, null=True)  # e.g. "ses", "twilio", "khalti_sms"
    provider_message_id = models.CharField(max_length=120, blank=True, null=True, db_index=True)

    last_error = models.TextField(blank=True, null=True)
    raw_response = models.JSONField(default=dict, blank=True)

    # optional generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, blank=True, null=True)
    object_id = models.CharField(max_length=64, blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        db_table = "outbound_messages"
        indexes = [
            models.Index(fields=["status", "scheduled_at"]),
            models.Index(fields=["channel", "status"]),
            models.Index(fields=["to", "created"]),
            models.Index(fields=["branch", "created"]),
        ]

    def __str__(self):
        return f"Outbound({self.channel}:{self.status})"


# ----------------------------- messaging (DMs / group chat) -----------------------------

class ThreadType(models.TextChoices):
    DIRECT = "direct", "Direct"
    GROUP = "group", "Group"
    COURSE = "course", "Course Discussion"
    SUPPORT = "support", "Support"


class MessageType(models.TextChoices):
    TEXT = "text", "Text"
    FILE = "file", "File"
    SYSTEM = "system", "System"


class MessageThread(BranchScopedStampedOwnedActive):
    """
    DM / group / course chat container.
    """

    thread_type = models.CharField(max_length=20, choices=ThreadType.choices, default=ThreadType.DIRECT, db_index=True)

    title = models.CharField(max_length=200, blank=True, null=True)
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="message_threads",
    )

    # denormalized last activity
    last_message_at = models.DateTimeField(blank=True, null=True, db_index=True)
    last_message_preview = models.CharField(max_length=200, blank=True, null=True)

    is_locked = models.BooleanField(default=False, db_index=True)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "message_threads"
        indexes = [
            models.Index(fields=["branch", "last_message_at"]),
            models.Index(fields=["thread_type"]),
            models.Index(fields=["course"]),
        ]

    def __str__(self):
        return f"Thread({self.id})"


class ThreadParticipant(StampedOwnedActive):
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name="participants", db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="message_threads", db_index=True)

    is_admin = models.BooleanField(default=False)
    muted_until = models.DateTimeField(blank=True, null=True)

    last_read_at = models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        db_table = "thread_participants"
        constraints = [
            models.UniqueConstraint(fields=["thread", "user"], name="uniq_thread_user")
        ]
        indexes = [
            models.Index(fields=["user", "last_read_at"]),
        ]

    def __str__(self):
        return f"{self.thread_id}::{self.user_id}"


class ThreadMessage(StampedOwnedActive):
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name="messages", db_index=True)

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sent_messages",
        db_index=True,
    )

    message_type = models.CharField(max_length=10, choices=MessageType.choices, default=MessageType.TEXT, db_index=True)

    text = models.TextField(blank=True, null=True)

    # attachments (simple MVP)
    file_url = models.URLField(blank=True, null=True)
    storage_key = models.CharField(max_length=255, blank=True, null=True)
    original_name = models.CharField(max_length=255, blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    size_bytes = models.BigIntegerField(blank=True, null=True)

    is_deleted = models.BooleanField(default=False, db_index=True)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "thread_messages"
        ordering = ["created"]
        indexes = [
            models.Index(fields=["thread", "created"]),
            models.Index(fields=["sender", "created"]),
        ]

    def __str__(self):
        return f"Msg({self.thread_id})"


# ----------------------------- preferences -----------------------------

class UserNotificationPreference(StampedOwnedActive):
    """
    Per-user toggles. Keep it simple for MVP.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_pref")

    in_app_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=False)

    # granular keys (optional): {"enrollment_created": {"email":true,"in_app":true}, ...}
    overrides = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "user_notification_preferences"

    def __str__(self):
        return f"NotifPref({self.user_id})"
