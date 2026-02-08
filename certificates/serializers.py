from core.utils.AdaptedBulkSerializer import BulkModelSerializer
from certificates.models import (
    CertificateTemplate,
    CertificateRule,
    CertificateIssue,
    CertificateEvent,
)


class CertificateTemplateSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CertificateTemplate
        fields = "__all__"


class CertificateRuleSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CertificateRule
        fields = "__all__"


class CertificateIssueSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CertificateIssue
        fields = "__all__"


class CertificateEventSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CertificateEvent
        fields = "__all__"
