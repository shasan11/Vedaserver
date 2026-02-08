from core.utils.BulkModelViewSet import BaseModelViewSet
from courses.models import (
    CourseCategory,
    CourseTag,
    Course,
    CourseTagging,
    CourseInstructor,
    CoursePricing,
    CourseOutcome,
    CourseRequirement,
    CourseTargetAudience,
    CourseFAQ,
    CourseReview,
)
from courses.serializers import (
    CourseCategorySerializer,
    CourseTagSerializer,
    CourseSerializer,
    CourseTaggingSerializer,
    CourseInstructorSerializer,
    CoursePricingSerializer,
    CourseOutcomeSerializer,
    CourseRequirementSerializer,
    CourseTargetAudienceSerializer,
    CourseFAQSerializer,
    CourseReviewSerializer,
)
from courses.filters import (
    CourseCategoryFilter,
    CourseTagFilter,
    CourseFilter,
    CourseTaggingFilter,
    CourseInstructorFilter,
    CoursePricingFilter,
    CourseOutcomeFilter,
    CourseRequirementFilter,
    CourseTargetAudienceFilter,
    CourseFAQFilter,
    CourseReviewFilter,
)


class CourseCategoryViewSet(BaseModelViewSet):
    queryset = CourseCategory.objects.all()
    serializer_class = CourseCategorySerializer
    filterset_class = CourseCategoryFilter
    search_fields = ["name", "slug"]
    ordering_fields = "__all__"


class CourseTagViewSet(BaseModelViewSet):
    queryset = CourseTag.objects.all()
    serializer_class = CourseTagSerializer
    filterset_class = CourseTagFilter
    search_fields = ["name", "slug"]
    ordering_fields = "__all__"


class CourseViewSet(BaseModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filterset_class = CourseFilter
    search_fields = ["title", "slug", "subtitle", "short_description"]
    ordering_fields = "__all__"


class CourseTaggingViewSet(BaseModelViewSet):
    queryset = CourseTagging.objects.all()
    serializer_class = CourseTaggingSerializer
    filterset_class = CourseTaggingFilter
    search_fields = []
    ordering_fields = "__all__"


class CourseInstructorViewSet(BaseModelViewSet):
    queryset = CourseInstructor.objects.all()
    serializer_class = CourseInstructorSerializer
    filterset_class = CourseInstructorFilter
    search_fields = ["user__email", "display_name", "headline"]
    ordering_fields = "__all__"


class CoursePricingViewSet(BaseModelViewSet):
    queryset = CoursePricing.objects.all()
    serializer_class = CoursePricingSerializer
    filterset_class = CoursePricingFilter
    search_fields = ["currency_code", "pricing_type"]
    ordering_fields = "__all__"


class CourseOutcomeViewSet(BaseModelViewSet):
    queryset = CourseOutcome.objects.all()
    serializer_class = CourseOutcomeSerializer
    filterset_class = CourseOutcomeFilter
    search_fields = ["text"]
    ordering_fields = "__all__"


class CourseRequirementViewSet(BaseModelViewSet):
    queryset = CourseRequirement.objects.all()
    serializer_class = CourseRequirementSerializer
    filterset_class = CourseRequirementFilter
    search_fields = ["text"]
    ordering_fields = "__all__"


class CourseTargetAudienceViewSet(BaseModelViewSet):
    queryset = CourseTargetAudience.objects.all()
    serializer_class = CourseTargetAudienceSerializer
    filterset_class = CourseTargetAudienceFilter
    search_fields = ["text"]
    ordering_fields = "__all__"


class CourseFAQViewSet(BaseModelViewSet):
    queryset = CourseFAQ.objects.all()
    serializer_class = CourseFAQSerializer
    filterset_class = CourseFAQFilter
    search_fields = ["question", "answer"]
    ordering_fields = "__all__"


class CourseReviewViewSet(BaseModelViewSet):
    queryset = CourseReview.objects.all()
    serializer_class = CourseReviewSerializer
    filterset_class = CourseReviewFilter
    search_fields = ["status", "note"]
    ordering_fields = "__all__"
