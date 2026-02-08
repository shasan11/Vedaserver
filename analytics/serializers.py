from core.utils.AdaptedBulkSerializer import BulkModelSerializer
from analytics.models import (
    AcquisitionCampaign,
    AnalyticsSession,
    AnalyticsEvent,
    DailyMetric,
    RetentionCohort,
)


class AcquisitionCampaignSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = AcquisitionCampaign
        fields = "__all__"


class AnalyticsSessionSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = AnalyticsSession
        fields = "__all__"


class AnalyticsEventSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = AnalyticsEvent
        fields = "__all__"


class DailyMetricSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = DailyMetric
        fields = "__all__"


class RetentionCohortSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = RetentionCohort
        fields = "__all__"
