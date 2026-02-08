from core.utils.AdaptedBulkSerializer import BulkModelSerializer
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


class SupportCategorySerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = SupportCategory
        fields = "__all__"


class SupportTagSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = SupportTag
        fields = "__all__"


class SupportSLASerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = SupportSLA
        fields = "__all__"


class SupportTicketSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = SupportTicket
        fields = "__all__"


class SupportTicketTagSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = SupportTicketTag
        fields = "__all__"


class SupportTicketWatcherSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = SupportTicketWatcher
        fields = "__all__"


class SupportTicketMessageSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = SupportTicketMessage
        fields = "__all__"


class SupportMessageAttachmentSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = SupportMessageAttachment
        fields = "__all__"


class SupportTicketEventSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = SupportTicketEvent
        fields = "__all__"


class CannedResponseSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CannedResponse
        fields = "__all__"


class KnowledgeBaseArticleSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = KnowledgeBaseArticle
        fields = "__all__"
