from core.utils.AdaptedBulkSerializer import BulkModelSerializer
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


class CourseCategorySerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CourseCategory
        fields = "__all__"


class CourseTagSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CourseTag
        fields = "__all__"


class CourseSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Course
        fields = "__all__"


class CourseTaggingSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CourseTagging
        fields = "__all__"


class CourseInstructorSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CourseInstructor
        fields = "__all__"


class CoursePricingSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CoursePricing
        fields = "__all__"


class CourseOutcomeSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CourseOutcome
        fields = "__all__"


class CourseRequirementSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CourseRequirement
        fields = "__all__"


class CourseTargetAudienceSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CourseTargetAudience
        fields = "__all__"


class CourseFAQSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CourseFAQ
        fields = "__all__"


class CourseReviewSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CourseReview
        fields = "__all__"
