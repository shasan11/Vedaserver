from core.utils.BulkModelViewSet import BaseModelViewSet
from analytics.models import (
    AcquisitionCampaign,
    AnalyticsSession,
    AnalyticsEvent,
    DailyMetric,
    RetentionCohort,
)
from analytics.serializers import (
    AcquisitionCampaignSerializer,
    AnalyticsSessionSerializer,
    AnalyticsEventSerializer,
    DailyMetricSerializer,
    RetentionCohortSerializer,
)
from analytics.filters import (
    AcquisitionCampaignFilter,
    AnalyticsSessionFilter,
    AnalyticsEventFilter,
    DailyMetricFilter,
    RetentionCohortFilter,
)


class AcquisitionCampaignViewSet(BaseModelViewSet):
    queryset = AcquisitionCampaign.objects.all()
    serializer_class = AcquisitionCampaignSerializer
    filterset_class = AcquisitionCampaignFilter
    search_fields = ["name", "source", "medium", "campaign", "content", "term"]
    ordering_fields = "__all__"


class AnalyticsSessionViewSet(BaseModelViewSet):
    queryset = AnalyticsSession.objects.all()
    serializer_class = AnalyticsSessionSerializer
    filterset_class = AnalyticsSessionFilter
    search_fields = ["session_key", "utm_source", "utm_medium", "utm_campaign", "device_os", "browser"]
    ordering_fields = "__all__"


class AnalyticsEventViewSet(BaseModelViewSet):
    queryset = AnalyticsEvent.objects.all()
    serializer_class = AnalyticsEventSerializer
    filterset_class = AnalyticsEventFilter
    search_fields = ["event_type", "name", "path", "page_title"]
    ordering_fields = "__all__"


class DailyMetricViewSet(BaseModelViewSet):
    queryset = DailyMetric.objects.all()
    serializer_class = DailyMetricSerializer
    filterset_class = DailyMetricFilter
    search_fields = ["metric"]
    ordering_fields = "__all__"


class RetentionCohortViewSet(BaseModelViewSet):
    queryset = RetentionCohort.objects.all()
    serializer_class = RetentionCohortSerializer
    filterset_class = RetentionCohortFilter
    search_fields = ["cohort_type"]
    ordering_fields = "__all__"
