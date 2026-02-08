from django.urls import path, include
from rest_framework_bulk.routes import BulkRouter

from support.views import (
    SupportCategoryViewSet,
    SupportTagViewSet,
    SupportSLAViewSet,
    SupportTicketViewSet,
    SupportTicketTagViewSet,
    SupportTicketWatcherViewSet,
    SupportTicketMessageViewSet,
    SupportMessageAttachmentViewSet,
    SupportTicketEventViewSet,
    CannedResponseViewSet,
    KnowledgeBaseArticleViewSet,
)

router = BulkRouter()
router.register(r"support-categories", SupportCategoryViewSet, basename="support-category")
router.register(r"support-tags", SupportTagViewSet, basename="support-tag")
router.register(r"support-slas", SupportSLAViewSet, basename="support-sla")
router.register(r"support-tickets", SupportTicketViewSet, basename="support-ticket")
router.register(r"support-ticket-tags", SupportTicketTagViewSet, basename="support-ticket-tag")
router.register(r"support-ticket-watchers", SupportTicketWatcherViewSet, basename="support-ticket-watcher")
router.register(r"support-ticket-messages", SupportTicketMessageViewSet, basename="support-ticket-message")
router.register(r"support-message-attachments", SupportMessageAttachmentViewSet, basename="support-message-attachment")
router.register(r"support-ticket-events", SupportTicketEventViewSet, basename="support-ticket-event")
router.register(r"canned-responses", CannedResponseViewSet, basename="canned-response")
router.register(r"knowledge-base-articles", KnowledgeBaseArticleViewSet, basename="knowledge-base-article")

urlpatterns = [
    path("", include(router.urls)),
]
