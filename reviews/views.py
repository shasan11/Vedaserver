from core.utils.BulkModelViewSet import BaseModelViewSet
from reviews.models import (
    CourseReview,
    ReviewReply,
    ReviewReaction,
    ReviewReport,
    CourseRatingSummary,
)
from reviews.serializers import (
    CourseReviewSerializer,
    ReviewReplySerializer,
    ReviewReactionSerializer,
    ReviewReportSerializer,
    CourseRatingSummarySerializer,
)
from reviews.filters import (
    CourseReviewFilter,
    ReviewReplyFilter,
    ReviewReactionFilter,
    ReviewReportFilter,
    CourseRatingSummaryFilter,
)


class CourseReviewViewSet(BaseModelViewSet):
    queryset = CourseReview.objects.all()
    serializer_class = CourseReviewSerializer
    filterset_class = CourseReviewFilter
    search_fields = ["title", "body", "status"]
    ordering_fields = "__all__"


class ReviewReplyViewSet(BaseModelViewSet):
    queryset = ReviewReply.objects.all()
    serializer_class = ReviewReplySerializer
    filterset_class = ReviewReplyFilter
    search_fields = ["message", "author__email"]
    ordering_fields = "__all__"


class ReviewReactionViewSet(BaseModelViewSet):
    queryset = ReviewReaction.objects.all()
    serializer_class = ReviewReactionSerializer
    filterset_class = ReviewReactionFilter
    search_fields = ["reaction_type"]
    ordering_fields = "__all__"


class ReviewReportViewSet(BaseModelViewSet):
    queryset = ReviewReport.objects.all()
    serializer_class = ReviewReportSerializer
    filterset_class = ReviewReportFilter
    search_fields = ["details", "status"]
    ordering_fields = "__all__"


class CourseRatingSummaryViewSet(BaseModelViewSet):
    queryset = CourseRatingSummary.objects.all()
    serializer_class = CourseRatingSummarySerializer
    filterset_class = CourseRatingSummaryFilter
    search_fields = []
    ordering_fields = "__all__"
