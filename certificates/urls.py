from django.urls import path, include
from rest_framework_bulk.routes import BulkRouter

from certificates.views import (
    CertificateTemplateViewSet,
    CertificateRuleViewSet,
    CertificateIssueViewSet,
    CertificateEventViewSet,
)

router = BulkRouter()
router.register(r"certificate-templates", CertificateTemplateViewSet, basename="certificate-template")
router.register(r"certificate-rules", CertificateRuleViewSet, basename="certificate-rule")
router.register(r"certificate-issues", CertificateIssueViewSet, basename="certificate-issue")
router.register(r"certificate-events", CertificateEventViewSet, basename="certificate-event")

urlpatterns = [
    path("", include(router.urls)),
]
