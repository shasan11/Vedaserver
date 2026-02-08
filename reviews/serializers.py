from core.utils.AdaptedBulkSerializer import BulkModelSerializer
from reviews.models import (
    CourseReview,
    ReviewReply,
    ReviewReaction,
    ReviewReport,
    CourseRatingSummary,
)


class CourseReviewSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CourseReview
        fields = "__all__"


class ReviewReplySerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = ReviewReply
        fields = "__all__"


class ReviewReactionSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = ReviewReaction
        fields = "__all__"


class ReviewReportSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = ReviewReport
        fields = "__all__"


class CourseRatingSummarySerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CourseRatingSummary
        fields = "__all__"
