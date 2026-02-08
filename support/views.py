from core.utils.BulkModelViewSet import BaseModelViewSet
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
from support.serializers import (
    SupportCategorySerializer,
    SupportTagSerializer,
    SupportSLASerializer,
    SupportTicketSerializer,
    SupportTicketTagSerializer,
    SupportTicketWatcherSerializer,
    SupportTicketMessageSerializer,
    SupportMessageAttachmentSerializer,
    SupportTicketEventSerializer,
    CannedResponseSerializer,
    KnowledgeBaseArticleSerializer,
)
from support.filters import (
    SupportCategoryFilter,
    SupportTagFilter,
    SupportSLAFilter,
    SupportTicketFilter,
    SupportTicketTagFilter,
    SupportTicketWatcherFilter,
    SupportTicketMessageFilter,
    SupportMessageAttachmentFilter,
    SupportTicketEventFilter,
    CannedResponseFilter,
    KnowledgeBaseArticleFilter,
)


class SupportCategoryViewSet(BaseModelViewSet):
    queryset = SupportCategory.objects.all()
    serializer_class = SupportCategorySerializer
    filterset_class = SupportCategoryFilter
    search_fields = ["name", "slug"]
    ordering_fields = "__all__"


class SupportTagViewSet(BaseModelViewSet):
    queryset = SupportTag.objects.all()
    serializer_class = SupportTagSerializer
    filterset_class = SupportTagFilter
    search_fields = ["name", "slug"]
    ordering_fields = "__all__"


class SupportSLAViewSet(BaseModelViewSet):
    queryset = SupportSLA.objects.all()
    serializer_class = SupportSLASerializer
    filterset_class = SupportSLAFilter
    search_fields = ["priority"]
    ordering_fields = "__all__"


class SupportTicketViewSet(BaseModelViewSet):
    queryset = SupportTicket.objects.all()
    serializer_class = SupportTicketSerializer
    filterset_class = SupportTicketFilter
    search_fields = ["ticket_no", "subject", "description"]
    ordering_fields = "__all__"


class SupportTicketTagViewSet(BaseModelViewSet):
    queryset = SupportTicketTag.objects.all()
    serializer_class = SupportTicketTagSerializer
    filterset_class = SupportTicketTagFilter
    search_fields = []
    ordering_fields = "__all__"


class SupportTicketWatcherViewSet(BaseModelViewSet):
    queryset = SupportTicketWatcher.objects.all()
    serializer_class = SupportTicketWatcherSerializer
    filterset_class = SupportTicketWatcherFilter
    search_fields = ["user__email"]
    ordering_fields = "__all__"


class SupportTicketMessageViewSet(BaseModelViewSet):
    queryset = SupportTicketMessage.objects.all()
    serializer_class = SupportTicketMessageSerializer
    filterset_class = SupportTicketMessageFilter
    search_fields = ["body"]
    ordering_fields = "__all__"


class SupportMessageAttachmentViewSet(BaseModelViewSet):
    queryset = SupportMessageAttachment.objects.all()
    serializer_class = SupportMessageAttachmentSerializer
    filterset_class = SupportMessageAttachmentFilter
    search_fields = ["original_name"]
    ordering_fields = "__all__"


class SupportTicketEventViewSet(BaseModelViewSet):
    queryset = SupportTicketEvent.objects.all()
    serializer_class = SupportTicketEventSerializer
    filterset_class = SupportTicketEventFilter
    search_fields = ["event_type", "message"]
    ordering_fields = "__all__"


class CannedResponseViewSet(BaseModelViewSet):
    queryset = CannedResponse.objects.all()
    serializer_class = CannedResponseSerializer
    filterset_class = CannedResponseFilter
    search_fields = ["title", "slug", "body"]
    ordering_fields = "__all__"


class KnowledgeBaseArticleViewSet(BaseModelViewSet):
    queryset = KnowledgeBaseArticle.objects.all()
    serializer_class = KnowledgeBaseArticleSerializer
    filterset_class = KnowledgeBaseArticleFilter
    search_fields = ["title", "slug", "summary"]
    ordering_fields = "__all__"
