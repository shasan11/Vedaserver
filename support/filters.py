import django_filters

from support.models import (
    SupportCategory,
    SupportTag,
    SupportSLA,
    SupportTicket,
    SupportTicketTag,
    SupportTicketWatcher,
    SupportTicketMessage,
    SupportMessageAttachment,
    SupportTicketEvent,
    CannedResponse,
    KnowledgeBaseArticle,
)


class SupportCategoryFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    slug = django_filters.CharFilter(lookup_expr="iexact")
    is_default = django_filters.BooleanFilter()
    active = django_filters.BooleanFilter()

    class Meta:
        model = SupportCategory
        fields = ["branch", "slug", "is_default", "active"]


class SupportTagFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    slug = django_filters.CharFilter(lookup_expr="iexact")
    active = django_filters.BooleanFilter()

    class Meta:
        model = SupportTag
        fields = ["branch", "slug", "active"]


class SupportSLAFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    priority = django_filters.CharFilter(lookup_expr="iexact")
    active = django_filters.BooleanFilter()

    class Meta:
        model = SupportSLA
        fields = ["branch", "priority", "active"]


class SupportTicketFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    status = django_filters.CharFilter(lookup_expr="iexact")
    priority = django_filters.CharFilter(lookup_expr="iexact")
    ticket_type = django_filters.CharFilter(lookup_expr="iexact")
    channel = django_filters.CharFilter(lookup_expr="iexact")
    reporter = django_filters.UUIDFilter(field_name="reporter_id")
    assigned_to = django_filters.UUIDFilter(field_name="assigned_to_id")
    category = django_filters.UUIDFilter(field_name="category_id")
    active = django_filters.BooleanFilter()

    class Meta:
        model = SupportTicket
        fields = [
            "branch",
            "status",
            "priority",
            "ticket_type",
            "channel",
            "reporter",
            "assigned_to",
            "category",
            "active",
        ]


class SupportTicketTagFilter(django_filters.FilterSet):
    ticket = django_filters.UUIDFilter(field_name="ticket_id")
    tag = django_filters.UUIDFilter(field_name="tag_id")

    class Meta:
        model = SupportTicketTag
        fields = ["ticket", "tag"]


class SupportTicketWatcherFilter(django_filters.FilterSet):
    ticket = django_filters.UUIDFilter(field_name="ticket_id")
    user = django_filters.UUIDFilter(field_name="user_id")

    class Meta:
        model = SupportTicketWatcher
        fields = ["ticket", "user"]


class SupportTicketMessageFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    ticket = django_filters.UUIDFilter(field_name="ticket_id")
    sender = django_filters.UUIDFilter(field_name="sender_id")
    message_type = django_filters.CharFilter(lookup_expr="iexact")
    is_internal = django_filters.BooleanFilter()

    class Meta:
        model = SupportTicketMessage
        fields = ["branch", "ticket", "sender", "message_type", "is_internal"]


class SupportMessageAttachmentFilter(django_filters.FilterSet):
    message = django_filters.UUIDFilter(field_name="message_id")

    class Meta:
        model = SupportMessageAttachment
        fields = ["message"]


class SupportTicketEventFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    ticket = django_filters.UUIDFilter(field_name="ticket_id")
    event_type = django_filters.CharFilter(lookup_expr="iexact")
    actor = django_filters.UUIDFilter(field_name="actor_id")

    class Meta:
        model = SupportTicketEvent
        fields = ["branch", "ticket", "event_type", "actor"]


class CannedResponseFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    slug = django_filters.CharFilter(lookup_expr="iexact")
    active = django_filters.BooleanFilter()

    class Meta:
        model = CannedResponse
        fields = ["branch", "slug", "active"]


class KnowledgeBaseArticleFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    slug = django_filters.CharFilter(lookup_expr="iexact")
    status = django_filters.CharFilter(lookup_expr="iexact")
    category = django_filters.UUIDFilter(field_name="category_id")
    active = django_filters.BooleanFilter()

    class Meta:
        model = KnowledgeBaseArticle
        fields = ["branch", "slug", "status", "category", "active"]
