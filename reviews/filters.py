import django_filters

from reviews.models import (
    CourseReview,
    ReviewReply,
    ReviewReaction,
    ReviewReport,
    CourseRatingSummary,
)


class CourseReviewFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    course = django_filters.UUIDFilter(field_name="course_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    enrollment = django_filters.UUIDFilter(field_name="enrollment_id")
    status = django_filters.CharFilter(lookup_expr="iexact")
    rating = django_filters.NumberFilter()

    class Meta:
        model = CourseReview
        fields = ["branch", "course", "user", "enrollment", "status", "rating"]


class ReviewReplyFilter(django_filters.FilterSet):
    review = django_filters.UUIDFilter(field_name="review_id")
    author = django_filters.UUIDFilter(field_name="author_id")
    is_official = django_filters.BooleanFilter()

    class Meta:
        model = ReviewReply
        fields = ["review", "author", "is_official"]


class ReviewReactionFilter(django_filters.FilterSet):
    review = django_filters.UUIDFilter(field_name="review_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    reaction_type = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = ReviewReaction
        fields = ["review", "user", "reaction_type"]


class ReviewReportFilter(django_filters.FilterSet):
    review = django_filters.UUIDFilter(field_name="review_id")
    reported_by = django_filters.UUIDFilter(field_name="reported_by_id")
    reason = django_filters.CharFilter(lookup_expr="iexact")
    status = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = ReviewReport
        fields = ["review", "reported_by", "reason", "status"]


class CourseRatingSummaryFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    course = django_filters.UUIDFilter(field_name="course_id")

    class Meta:
        model = CourseRatingSummary
        fields = ["branch", "course"]
