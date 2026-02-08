import django_filters

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


class CourseCategoryFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    name = django_filters.CharFilter(lookup_expr="icontains")
    slug = django_filters.CharFilter(lookup_expr="iexact")
    parent = django_filters.UUIDFilter(field_name="parent_id")
    active = django_filters.BooleanFilter()

    class Meta:
        model = CourseCategory
        fields = ["branch", "name", "slug", "parent", "active"]


class CourseTagFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    name = django_filters.CharFilter(lookup_expr="icontains")
    slug = django_filters.CharFilter(lookup_expr="iexact")
    active = django_filters.BooleanFilter()

    class Meta:
        model = CourseTag
        fields = ["branch", "name", "slug", "active"]


class CourseFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    category = django_filters.UUIDFilter(field_name="category_id")
    status = django_filters.CharFilter(lookup_expr="iexact")
    visibility = django_filters.CharFilter(lookup_expr="iexact")
    slug = django_filters.CharFilter(lookup_expr="iexact")
    level = django_filters.CharFilter(lookup_expr="iexact")
    is_featured = django_filters.BooleanFilter()
    active = django_filters.BooleanFilter()

    class Meta:
        model = Course
        fields = ["branch", "category", "status", "visibility", "slug", "level", "is_featured", "active"]


class CourseTaggingFilter(django_filters.FilterSet):
    course = django_filters.UUIDFilter(field_name="course_id")
    tag = django_filters.UUIDFilter(field_name="tag_id")

    class Meta:
        model = CourseTagging
        fields = ["course", "tag"]


class CourseInstructorFilter(django_filters.FilterSet):
    course = django_filters.UUIDFilter(field_name="course_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    role = django_filters.CharFilter(lookup_expr="iexact")
    is_primary = django_filters.BooleanFilter()

    class Meta:
        model = CourseInstructor
        fields = ["course", "user", "role", "is_primary"]


class CoursePricingFilter(django_filters.FilterSet):
    course = django_filters.UUIDFilter(field_name="course_id")
    pricing_type = django_filters.CharFilter(lookup_expr="iexact")
    currency_code = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = CoursePricing
        fields = ["course", "pricing_type", "currency_code"]


class CourseOutcomeFilter(django_filters.FilterSet):
    course = django_filters.UUIDFilter(field_name="course_id")

    class Meta:
        model = CourseOutcome
        fields = ["course"]


class CourseRequirementFilter(django_filters.FilterSet):
    course = django_filters.UUIDFilter(field_name="course_id")

    class Meta:
        model = CourseRequirement
        fields = ["course"]


class CourseTargetAudienceFilter(django_filters.FilterSet):
    course = django_filters.UUIDFilter(field_name="course_id")

    class Meta:
        model = CourseTargetAudience
        fields = ["course"]


class CourseFAQFilter(django_filters.FilterSet):
    course = django_filters.UUIDFilter(field_name="course_id")

    class Meta:
        model = CourseFAQ
        fields = ["course"]


class CourseReviewFilter(django_filters.FilterSet):
    course = django_filters.UUIDFilter(field_name="course_id")
    status = django_filters.CharFilter(lookup_expr="iexact")
    requested_by = django_filters.UUIDFilter(field_name="requested_by_id")
    reviewed_by = django_filters.UUIDFilter(field_name="reviewed_by_id")

    class Meta:
        model = CourseReview
        fields = ["course", "status", "requested_by", "reviewed_by"]
