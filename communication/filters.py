import django_filters

from communication.models import (
    MessageTemplate,
    Announcement,
    AnnouncementTargetUser,
    Notification,
    OutboundMessage,
    MessageThread,
    ThreadParticipant,
    ThreadMessage,
    UserNotificationPreference,
)


class MessageTemplateFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    key = django_filters.CharFilter(lookup_expr="iexact")
    channel = django_filters.CharFilter(lookup_expr="iexact")
    active = django_filters.BooleanFilter()

    class Meta:
        model = MessageTemplate
        fields = ["branch", "key", "channel", "active"]


class AnnouncementFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    status = django_filters.CharFilter(lookup_expr="iexact")
    audience_type = django_filters.CharFilter(lookup_expr="iexact")
    course = django_filters.UUIDFilter(field_name="course_id")
    is_pinned = django_filters.BooleanFilter()
    active = django_filters.BooleanFilter()

    class Meta:
        model = Announcement
        fields = ["branch", "status", "audience_type", "course", "is_pinned", "active"]


class AnnouncementTargetUserFilter(django_filters.FilterSet):
    announcement = django_filters.UUIDFilter(field_name="announcement_id")
    user = django_filters.UUIDFilter(field_name="user_id")

    class Meta:
        model = AnnouncementTargetUser
        fields = ["announcement", "user"]


class NotificationFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    status = django_filters.CharFilter(lookup_expr="iexact")
    priority = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Notification
        fields = ["branch", "user", "status", "priority"]


class OutboundMessageFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    channel = django_filters.CharFilter(lookup_expr="iexact")
    status = django_filters.CharFilter(lookup_expr="iexact")
    user = django_filters.UUIDFilter(field_name="user_id")
    template_key = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = OutboundMessage
        fields = ["branch", "channel", "status", "user", "template_key"]


class MessageThreadFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    thread_type = django_filters.CharFilter(lookup_expr="iexact")
    course = django_filters.UUIDFilter(field_name="course_id")
    is_locked = django_filters.BooleanFilter()
    active = django_filters.BooleanFilter()

    class Meta:
        model = MessageThread
        fields = ["branch", "thread_type", "course", "is_locked", "active"]


class ThreadParticipantFilter(django_filters.FilterSet):
    thread = django_filters.UUIDFilter(field_name="thread_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    is_admin = django_filters.BooleanFilter()

    class Meta:
        model = ThreadParticipant
        fields = ["thread", "user", "is_admin"]


class ThreadMessageFilter(django_filters.FilterSet):
    thread = django_filters.UUIDFilter(field_name="thread_id")
    sender = django_filters.UUIDFilter(field_name="sender_id")
    message_type = django_filters.CharFilter(lookup_expr="iexact")
    is_deleted = django_filters.BooleanFilter()

    class Meta:
        model = ThreadMessage
        fields = ["thread", "sender", "message_type", "is_deleted"]


class UserNotificationPreferenceFilter(django_filters.FilterSet):
    user = django_filters.UUIDFilter(field_name="user_id")

    class Meta:
        model = UserNotificationPreference
        fields = ["user"]
