from django.urls import path, include
from rest_framework_bulk.routes import BulkRouter

from reviews.views import (
    CourseReviewViewSet,
    ReviewReplyViewSet,
    ReviewReactionViewSet,
    ReviewReportViewSet,
    CourseRatingSummaryViewSet,
)

router = BulkRouter()
router.register(r"course-reviews", CourseReviewViewSet, basename="course-review")
router.register(r"review-replies", ReviewReplyViewSet, basename="review-reply")
router.register(r"review-reactions", ReviewReactionViewSet, basename="review-reaction")
router.register(r"review-reports", ReviewReportViewSet, basename="review-report")
router.register(r"course-rating-summaries", CourseRatingSummaryViewSet, basename="course-rating-summary")

urlpatterns = [
    path("", include(router.urls)),
]
