from django.urls import path, include
from rest_framework_bulk.routes import BulkRouter

from analytics.views import (
    AcquisitionCampaignViewSet,
    AnalyticsSessionViewSet,
    AnalyticsEventViewSet,
    DailyMetricViewSet,
    RetentionCohortViewSet,
)

router = BulkRouter()
router.register(r"acquisition-campaigns", AcquisitionCampaignViewSet, basename="acquisition-campaign")
router.register(r"analytics-sessions", AnalyticsSessionViewSet, basename="analytics-session")
router.register(r"analytics-events", AnalyticsEventViewSet, basename="analytics-event")
router.register(r"daily-metrics", DailyMetricViewSet, basename="daily-metric")
router.register(r"retention-cohorts", RetentionCohortViewSet, basename="retention-cohort")

urlpatterns = [
    path("", include(router.urls)),
]
