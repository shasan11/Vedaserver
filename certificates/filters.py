import django_filters

from certificates.models import (
    CertificateTemplate,
    CertificateRule,
    CertificateIssue,
    CertificateEvent,
)


class CertificateTemplateFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    course = django_filters.UUIDFilter(field_name="course_id")
    status = django_filters.CharFilter(lookup_expr="iexact")
    slug = django_filters.CharFilter(lookup_expr="iexact")
    is_default = django_filters.BooleanFilter()
    active = django_filters.BooleanFilter()

    class Meta:
        model = CertificateTemplate
        fields = ["branch", "course", "status", "slug", "is_default", "active"]


class CertificateRuleFilter(django_filters.FilterSet):
    course = django_filters.UUIDFilter(field_name="course_id")

    class Meta:
        model = CertificateRule
        fields = ["course"]


class CertificateIssueFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    course = django_filters.UUIDFilter(field_name="course_id")
    enrollment = django_filters.UUIDFilter(field_name="enrollment_id")
    template = django_filters.UUIDFilter(field_name="template_id")
    status = django_filters.CharFilter(lookup_expr="iexact")
    certificate_no = django_filters.CharFilter(lookup_expr="iexact")
    verification_code = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = CertificateIssue
        fields = [
            "branch",
            "user",
            "course",
            "enrollment",
            "template",
            "status",
            "certificate_no",
            "verification_code",
        ]


class CertificateEventFilter(django_filters.FilterSet):
    certificate = django_filters.UUIDFilter(field_name="certificate_id")
    event_type = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = CertificateEvent
        fields = ["certificate", "event_type"]
