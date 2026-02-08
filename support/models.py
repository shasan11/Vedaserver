# support/models.py
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from core.utils.coreModels import UUIDPk, StampedOwnedActive, BranchScopedStampedOwnedActive


# ----------------------------- lean base for high-write tables -----------------------------

class SupportStamped(UUIDPk):
    """
    Lean model for high-write tables (ticket messages/events).
    No history/user_add to avoid DB bloat.
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

class TicketStatus(models.TextChoices):
    OPEN = "open", "Open"
    IN_PROGRESS = "in_progress", "In progress"
    WAITING_ON_USER = "waiting_on_user", "Waiting on user"
    WAITING_ON_SUPPORT = "waiting_on_support", "Waiting on support"
    RESOLVED = "resolved", "Resolved"
    CLOSED = "closed", "Closed"
    SPAM = "spam", "Spam"


class TicketPriority(models.TextChoices):
    LOW = "low", "Low"
    NORMAL = "normal", "Normal"
    HIGH = "high", "High"
    URGENT = "urgent", "Urgent"


class TicketChannel(models.TextChoices):
    IN_APP = "in_app", "In-app"
    EMAIL = "email", "Email"
    WHATSAPP = "whatsapp", "WhatsApp"
    PHONE = "phone", "Phone"
    ADMIN = "admin", "Admin-created"


class TicketType(models.TextChoices):
    QUESTION = "question", "Question"
    BUG = "bug", "Bug"
    BILLING = "billing", "Billing"
    CONTENT = "content", "Content issue"
    TECHNICAL = "technical", "Technical"
    FEATURE_REQUEST = "feature_request", "Feature request"
    OTHER = "other", "Other"


class MessageType(models.TextChoices):
    TEXT = "text", "Text"
    SYSTEM = "system", "System"
    NOTE = "note", "Internal note"
    FILE = "file", "File"


class EventType(models.TextChoices):
    CREATED = "created", "Created"
    ASSIGNED = "assigned", "Assigned"
    UNASSIGNED = "unassigned", "Unassigned"
    STATUS_CHANGED = "status_changed", "Status changed"
    PRIORITY_CHANGED = "priority_changed", "Priority changed"
    TAG_ADDED = "tag_added", "Tag added"
    TAG_REMOVED = "tag_removed", "Tag removed"
    MERGED = "merged", "Merged"
    REOPENED = "reopened", "Reopened"
    RESOLVED = "resolved", "Resolved"
    CLOSED = "closed", "Closed"
    NOTE = "note", "Note"


# ----------------------------- taxonomy -----------------------------

class SupportCategory(BranchScopedStampedOwnedActive):
    name = models.CharField(max_length=120, db_index=True)
    slug = models.SlugField(max_length=140, db_index=True)
    description = models.TextField(blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_default = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "support_categories"
        ordering = ["sort_order", "name"]
        constraints = [
            models.UniqueConstraint(fields=["branch", "slug"], name="uniq_support_category_branch_slug")
        ]
        indexes = [
            models.Index(fields=["branch", "active"]),
        ]

    def __str__(self):
        return self.name


class SupportTag(BranchScopedStampedOwnedActive):
    name = models.CharField(max_length=80, db_index=True)
    slug = models.SlugField(max_length=100, db_index=True)

    class Meta:
        db_table = "support_tags"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["branch", "slug"], name="uniq_support_tag_branch_slug")
        ]

    def __str__(self):
        return self.name


# ----------------------------- SLA (optional but worth it) -----------------------------

class SupportSLA(BranchScopedStampedOwnedActive):
    """
    SLA policy per priority.
    Example:
      - urgent: response 30 min, resolution 4 hours
      - normal: response 4 hours, resolution 48 hours
    """
    priority = models.CharField(max_length=10, choices=TicketPriority.choices, unique=False, db_index=True)

    first_response_minutes = models.PositiveIntegerField(default=240, validators=[MinValueValidator(1)])
    resolution_minutes = models.PositiveIntegerField(default=2880, validators=[MinValueValidator(1)])

    class Meta:
        db_table = "support_slas"
        constraints = [
            models.UniqueConstraint(fields=["branch", "priority"], name="uniq_support_sla_branch_priority")
        ]
        indexes = [
            models.Index(fields=["branch", "priority"]),
        ]

    def __str__(self):
        return f"SLA({self.priority})"


# ----------------------------- ticket -----------------------------

class SupportTicket(BranchScopedStampedOwnedActive):
    """
    Core support ticket. Threaded conversation lives in SupportTicketMessage.
    """

    ticket_no = models.CharField(max_length=60, blank=True, null=True, db_index=True)

    subject = models.CharField(max_length=220, db_index=True)
    description = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=TicketStatus.choices, default=TicketStatus.OPEN, db_index=True)
    priority = models.CharField(max_length=10, choices=TicketPriority.choices, default=TicketPriority.NORMAL, db_index=True)
    ticket_type = models.CharField(max_length=20, choices=TicketType.choices, default=TicketType.QUESTION, db_index=True)

    channel = models.CharField(max_length=20, choices=TicketChannel.choices, default=TicketChannel.IN_APP, db_index=True)

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="support_tickets_reported",
        db_index=True,
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="support_tickets_assigned",
        db_index=True,
    )

    category = models.ForeignKey(
        SupportCategory,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="tickets",
        db_index=True,
    )

    tags = models.ManyToManyField(SupportTag, through="SupportTicketTag", blank=True, related_name="tickets")

    # Link to any object: Enrollment, Order, Course, Lesson, etc.
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, blank=True, null=True)
    object_id = models.CharField(max_length=64, blank=True, null=True)  # UUID/string
    content_object = GenericForeignKey("content_type", "object_id")

    # SLA fields (snapshotted)
    sla_first_response_due_at = models.DateTimeField(blank=True, null=True, db_index=True)
    sla_resolution_due_at = models.DateTimeField(blank=True, null=True, db_index=True)
    first_response_at = models.DateTimeField(blank=True, null=True, db_index=True)
    resolved_at = models.DateTimeField(blank=True, null=True, db_index=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    # denormalized for fast list UI
    last_message_at = models.DateTimeField(blank=True, null=True, db_index=True)
    last_message_preview = models.CharField(max_length=220, blank=True, null=True)
    last_message_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="support_last_messages",
    )

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "support_tickets"
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["branch", "priority"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["reporter", "status"]),
            models.Index(fields=["status", "last_message_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["branch", "ticket_no"],
                name="uniq_support_ticket_branch_ticket_no",
            )
        ]

    def __str__(self):
        return f"Ticket({self.ticket_no or self.id})"

    def touch_last_message(self, by_user=None, preview=None):
        now = timezone.now()
        self.last_message_at = now
        if by_user:
            self.last_message_by = by_user
        if preview:
            self.last_message_preview = preview[:220]
        # first response tracking
        if not self.first_response_at and by_user and by_user_id_safe(by_user) != by_user_id_safe(self.reporter):
            self.first_response_at = now
        self.save(update_fields=["last_message_at", "last_message_by", "last_message_preview", "first_response_at", "updated"])


def by_user_id_safe(user):
    try:
        return str(user.id)
    except Exception:
        return None


class SupportTicketTag(StampedOwnedActive):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="tag_links", db_index=True)
    tag = models.ForeignKey(SupportTag, on_delete=models.CASCADE, related_name="ticket_links", db_index=True)

    class Meta:
        db_table = "support_ticket_tags"
        constraints = [
            models.UniqueConstraint(fields=["ticket", "tag"], name="uniq_support_ticket_tag")
        ]


class SupportTicketWatcher(StampedOwnedActive):
    """
    Watchers get notified on updates.
    """
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="watchers", db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watched_tickets", db_index=True)

    class Meta:
        db_table = "support_ticket_watchers"
        constraints = [
            models.UniqueConstraint(fields=["ticket", "user"], name="uniq_support_ticket_watcher")
        ]


# ----------------------------- ticket messages -----------------------------

class SupportTicketMessage(SupportStamped, BranchBound):
    """
    Thread messages. High volume → lean.
    """

    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="messages", db_index=True)

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="support_messages_sent",
        db_index=True,
    )

    message_type = models.CharField(max_length=10, choices=MessageType.choices, default=MessageType.TEXT, db_index=True)

    body = models.TextField(blank=True, null=True)

    # Internal notes are visible to staff only
    is_internal = models.BooleanField(default=False, db_index=True)

    # quick attachments (optional)
    file_url = models.URLField(blank=True, null=True)
    storage_key = models.CharField(max_length=255, blank=True, null=True)
    original_name = models.CharField(max_length=255, blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    size_bytes = models.BigIntegerField(blank=True, null=True)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "support_ticket_messages"
        ordering = ["created"]
        indexes = [
            models.Index(fields=["ticket", "created"]),
            models.Index(fields=["branch", "created"]),
            models.Index(fields=["sender", "created"]),
            models.Index(fields=["ticket", "is_internal"]),
        ]

    def __str__(self):
        return f"Msg({self.ticket_id})"

    def save(self, *args, **kwargs):
        if self.ticket_id and self.branch_id is None:
            self.branch = self.ticket.branch
        super().save(*args, **kwargs)


# ----------------------------- message attachments (optional separate) -----------------------------

class SupportMessageAttachment(StampedOwnedActive):
    """
    If you want multiple files per message, use this table.
    (If not needed, skip it and use the fields on SupportTicketMessage.)
    """
    message = models.ForeignKey(SupportTicketMessage, on_delete=models.CASCADE, related_name="attachments", db_index=True)

    file_url = models.URLField(blank=True, null=True)
    storage_key = models.CharField(max_length=255, blank=True, null=True)

    original_name = models.CharField(max_length=255, blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    size_bytes = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = "support_message_attachments"
        indexes = [
            models.Index(fields=["message"]),
        ]

    def __str__(self):
        return f"Attach({self.message_id})"


# ----------------------------- ticket events (audit) -----------------------------

class SupportTicketEvent(SupportStamped, BranchBound):
    """
    Light audit trail of changes (status/assignment/etc.).
    """
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="events", db_index=True)

    event_type = models.CharField(max_length=30, choices=EventType.choices, db_index=True)
    message = models.CharField(max_length=255, blank=True, null=True)
    data = models.JSONField(default=dict, blank=True)

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="support_events_actor",
        db_index=True,
    )

    class Meta:
        db_table = "support_ticket_events"
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["ticket", "created"]),
            models.Index(fields=["branch", "created"]),
            models.Index(fields=["event_type", "created"]),
        ]

    def __str__(self):
        return f"Event({self.ticket_id}:{self.event_type})"

    def save(self, *args, **kwargs):
        if self.ticket_id and self.branch_id is None:
            self.branch = self.ticket.branch
        super().save(*args, **kwargs)


# ----------------------------- canned responses (staff productivity) -----------------------------

class CannedResponse(BranchScopedStampedOwnedActive):
    """
    Pre-written replies for support team.
    """
    title = models.CharField(max_length=160, db_index=True)
    slug = models.SlugField(max_length=180, db_index=True)

    # Use {{var}} placeholders and render in service layer
    body = models.TextField()

    tags = models.JSONField(default=list, blank=True)  # quick search tags in UI

    class Meta:
        db_table = "support_canned_responses"
        constraints = [
            models.UniqueConstraint(fields=["branch", "slug"], name="uniq_support_canned_response_branch_slug")
        ]
        indexes = [
            models.Index(fields=["branch", "active"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return self.title


# ----------------------------- knowledge base (optional) -----------------------------

class KBStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class KnowledgeBaseArticle(BranchScopedStampedOwnedActive):
    """
    Basic Help Center articles. Optional but super useful.
    """
    title = models.CharField(max_length=220, db_index=True)
    slug = models.SlugField(max_length=240, db_index=True)

    status = models.CharField(max_length=20, choices=KBStatus.choices, default=KBStatus.DRAFT, db_index=True)

    summary = models.CharField(max_length=400, blank=True, null=True)
    body = models.TextField(blank=True, null=True)

    category = models.ForeignKey(
        SupportCategory,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="kb_articles",
    )

    published_at = models.DateTimeField(blank=True, null=True, db_index=True)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "kb_articles"
        constraints = [
            models.UniqueConstraint(fields=["branch", "slug"], name="uniq_kb_article_branch_slug")
        ]
        indexes = [
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["status", "published_at"]),
        ]

    def __str__(self):
        return self.title
