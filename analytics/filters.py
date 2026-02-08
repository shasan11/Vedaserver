import django_filters

from analytics.models import (
    AcquisitionCampaign,
    AnalyticsSession,
    AnalyticsEvent,
    DailyMetric,
    RetentionCohort,
)


class AcquisitionCampaignFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    source = django_filters.CharFilter(lookup_expr="iexact")
    medium = django_filters.CharFilter(lookup_expr="iexact")
    campaign = django_filters.CharFilter(lookup_expr="iexact")
    active = django_filters.BooleanFilter()

    class Meta:
        model = AcquisitionCampaign
        fields = ["name", "source", "medium", "campaign", "active"]


class AnalyticsSessionFilter(django_filters.FilterSet):
    session_key = django_filters.CharFilter(lookup_expr="iexact")
    user = django_filters.UUIDFilter(field_name="user_id")
    status = django_filters.CharFilter(lookup_expr="iexact")
    branch = django_filters.UUIDFilter(field_name="branch_id")
    device_type = django_filters.CharFilter(lookup_expr="iexact")
    utm_source = django_filters.CharFilter(lookup_expr="iexact")
    utm_medium = django_filters.CharFilter(lookup_expr="iexact")
    utm_campaign = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = AnalyticsSession
        fields = [
            "session_key",
            "user",
            "status",
            "branch",
            "device_type",
            "utm_source",
            "utm_medium",
            "utm_campaign",
        ]


class AnalyticsEventFilter(django_filters.FilterSet):
    session = django_filters.UUIDFilter(field_name="session_id")
    event_type = django_filters.CharFilter(lookup_expr="iexact")
    user = django_filters.UUIDFilter(field_name="user_id")
    course = django_filters.UUIDFilter(field_name="course_id")
    lesson = django_filters.UUIDFilter(field_name="lesson_id")
    enrollment = django_filters.UUIDFilter(field_name="enrollment_id")
    order = django_filters.UUIDFilter(field_name="order_id")
    branch = django_filters.UUIDFilter(field_name="branch_id")

    class Meta:
        model = AnalyticsEvent
        fields = ["session", "event_type", "user", "course", "lesson", "enrollment", "order", "branch"]


class DailyMetricFilter(django_filters.FilterSet):
    date = django_filters.DateFilter()
    metric = django_filters.CharFilter(lookup_expr="iexact")
    course = django_filters.UUIDFilter(field_name="course_id")
    campaign = django_filters.UUIDFilter(field_name="campaign_id")
    branch = django_filters.UUIDFilter(field_name="branch_id")

    class Meta:
        model = DailyMetric
        fields = ["date", "metric", "course", "campaign", "branch"]


class RetentionCohortFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    cohort_type = django_filters.CharFilter(lookup_expr="iexact")
    cohort_date = django_filters.DateFilter()
    course = django_filters.UUIDFilter(field_name="course_id")
    active = django_filters.BooleanFilter()

    class Meta:
        model = RetentionCohort
        fields = ["branch", "cohort_type", "cohort_date", "course", "active"]
