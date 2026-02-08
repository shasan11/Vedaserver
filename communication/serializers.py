from core.utils.AdaptedBulkSerializer import BulkModelSerializer
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


class MessageTemplateSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = MessageTemplate
        fields = "__all__"


class AnnouncementSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Announcement
        fields = "__all__"


class AnnouncementTargetUserSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = AnnouncementTargetUser
        fields = "__all__"


class NotificationSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Notification
        fields = "__all__"


class OutboundMessageSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = OutboundMessage
        fields = "__all__"


class MessageThreadSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = MessageThread
        fields = "__all__"


class ThreadParticipantSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = ThreadParticipant
        fields = "__all__"


class ThreadMessageSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = ThreadMessage
        fields = "__all__"


class UserNotificationPreferenceSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = UserNotificationPreference
        fields = "__all__"
