from django.urls import path, include
from rest_framework_bulk.routes import BulkRouter

from communication.views import (
    MessageTemplateViewSet,
    AnnouncementViewSet,
    AnnouncementTargetUserViewSet,
    NotificationViewSet,
    OutboundMessageViewSet,
    MessageThreadViewSet,
    ThreadParticipantViewSet,
    ThreadMessageViewSet,
    UserNotificationPreferenceViewSet,
)

router = BulkRouter()
router.register(r"message-templates", MessageTemplateViewSet, basename="message-template")
router.register(r"announcements", AnnouncementViewSet, basename="announcement")
router.register(r"announcement-target-users", AnnouncementTargetUserViewSet, basename="announcement-target-user")
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"outbound-messages", OutboundMessageViewSet, basename="outbound-message")
router.register(r"message-threads", MessageThreadViewSet, basename="message-thread")
router.register(r"thread-participants", ThreadParticipantViewSet, basename="thread-participant")
router.register(r"thread-messages", ThreadMessageViewSet, basename="thread-message")
router.register(r"user-notification-preferences", UserNotificationPreferenceViewSet, basename="user-notification-preference")

urlpatterns = [
    path("", include(router.urls)),
]
