from core.utils.BulkModelViewSet import BaseModelViewSet
from certificates.models import (
    CertificateTemplate,
    CertificateRule,
    CertificateIssue,
    CertificateEvent,
)
from certificates.serializers import (
    CertificateTemplateSerializer,
    CertificateRuleSerializer,
    CertificateIssueSerializer,
    CertificateEventSerializer,
)
from certificates.filters import (
    CertificateTemplateFilter,
    CertificateRuleFilter,
    CertificateIssueFilter,
    CertificateEventFilter,
)


class CertificateTemplateViewSet(BaseModelViewSet):
    queryset = CertificateTemplate.objects.all()
    serializer_class = CertificateTemplateSerializer
    filterset_class = CertificateTemplateFilter
    search_fields = ["name", "slug", "title_text"]
    ordering_fields = "__all__"


class CertificateRuleViewSet(BaseModelViewSet):
    queryset = CertificateRule.objects.all()
    serializer_class = CertificateRuleSerializer
    filterset_class = CertificateRuleFilter
    search_fields = []
    ordering_fields = "__all__"


class CertificateIssueViewSet(BaseModelViewSet):
    queryset = CertificateIssue.objects.all()
    serializer_class = CertificateIssueSerializer
    filterset_class = CertificateIssueFilter
    search_fields = ["certificate_no", "verification_code", "student_name", "course_title"]
    ordering_fields = "__all__"


class CertificateEventViewSet(BaseModelViewSet):
    queryset = CertificateEvent.objects.all()
    serializer_class = CertificateEventSerializer
    filterset_class = CertificateEventFilter
    search_fields = ["event_type", "message"]
    ordering_fields = "__all__"
