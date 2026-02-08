from core.utils.BulkModelViewSet import BaseModelViewSet
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
from communication.serializers import (
    MessageTemplateSerializer,
    AnnouncementSerializer,
    AnnouncementTargetUserSerializer,
    NotificationSerializer,
    OutboundMessageSerializer,
    MessageThreadSerializer,
    ThreadParticipantSerializer,
    ThreadMessageSerializer,
    UserNotificationPreferenceSerializer,
)
from communication.filters import (
    MessageTemplateFilter,
    AnnouncementFilter,
    AnnouncementTargetUserFilter,
    NotificationFilter,
    OutboundMessageFilter,
    MessageThreadFilter,
    ThreadParticipantFilter,
    ThreadMessageFilter,
    UserNotificationPreferenceFilter,
)


class MessageTemplateViewSet(BaseModelViewSet):
    queryset = MessageTemplate.objects.all()
    serializer_class = MessageTemplateSerializer
    filterset_class = MessageTemplateFilter
    search_fields = ["key", "name", "subject"]
    ordering_fields = "__all__"


class AnnouncementViewSet(BaseModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    filterset_class = AnnouncementFilter
    search_fields = ["title", "body"]
    ordering_fields = "__all__"


class AnnouncementTargetUserViewSet(BaseModelViewSet):
    queryset = AnnouncementTargetUser.objects.all()
    serializer_class = AnnouncementTargetUserSerializer
    filterset_class = AnnouncementTargetUserFilter
    search_fields = ["user__email"]
    ordering_fields = "__all__"


class NotificationViewSet(BaseModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filterset_class = NotificationFilter
    search_fields = ["title", "body", "user__email"]
    ordering_fields = "__all__"


class OutboundMessageViewSet(BaseModelViewSet):
    queryset = OutboundMessage.objects.all()
    serializer_class = OutboundMessageSerializer
    filterset_class = OutboundMessageFilter
    search_fields = ["to", "subject", "template_key"]
    ordering_fields = "__all__"


class MessageThreadViewSet(BaseModelViewSet):
    queryset = MessageThread.objects.all()
    serializer_class = MessageThreadSerializer
    filterset_class = MessageThreadFilter
    search_fields = ["title"]
    ordering_fields = "__all__"


class ThreadParticipantViewSet(BaseModelViewSet):
    queryset = ThreadParticipant.objects.all()
    serializer_class = ThreadParticipantSerializer
    filterset_class = ThreadParticipantFilter
    search_fields = ["user__email"]
    ordering_fields = "__all__"


class ThreadMessageViewSet(BaseModelViewSet):
    queryset = ThreadMessage.objects.all()
    serializer_class = ThreadMessageSerializer
    filterset_class = ThreadMessageFilter
    search_fields = ["text"]
    ordering_fields = "__all__"


class UserNotificationPreferenceViewSet(BaseModelViewSet):
    queryset = UserNotificationPreference.objects.all()
    serializer_class = UserNotificationPreferenceSerializer
    filterset_class = UserNotificationPreferenceFilter
    search_fields = ["user__email"]
    ordering_fields = "__all__"
