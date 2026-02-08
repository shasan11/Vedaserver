import django_filters

from enrollments.models import (
    CourseCohort,
    Enrollment,
    EnrollmentAccessOverride,
    CourseAccessInvite,
    EnrollmentEvent,
)


class CourseCohortFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    course = django_filters.UUIDFilter(field_name="course_id")
    code = django_filters.CharFilter(lookup_expr="iexact")
    is_open = django_filters.BooleanFilter()
    is_default = django_filters.BooleanFilter()
    active = django_filters.BooleanFilter()

    class Meta:
        model = CourseCohort
        fields = ["branch", "course", "code", "is_open", "is_default", "active"]


class EnrollmentFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    course = django_filters.UUIDFilter(field_name="course_id")
    cohort = django_filters.UUIDFilter(field_name="cohort_id")
    status = django_filters.CharFilter(lookup_expr="iexact")
    source = django_filters.CharFilter(lookup_expr="iexact")
    access_type = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Enrollment
        fields = ["branch", "user", "course", "cohort", "status", "source", "access_type"]


class EnrollmentAccessOverrideFilter(django_filters.FilterSet):
    enrollment = django_filters.UUIDFilter(field_name="enrollment_id")

    class Meta:
        model = EnrollmentAccessOverride
        fields = ["enrollment"]


class CourseAccessInviteFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    course = django_filters.UUIDFilter(field_name="course_id")
    cohort = django_filters.UUIDFilter(field_name="cohort_id")
    email = django_filters.CharFilter(lookup_expr="iexact")
    status = django_filters.CharFilter(lookup_expr="iexact")
    token = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = CourseAccessInvite
        fields = ["branch", "course", "cohort", "email", "status", "token"]


class EnrollmentEventFilter(django_filters.FilterSet):
    enrollment = django_filters.UUIDFilter(field_name="enrollment_id")
    event_type = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = EnrollmentEvent
        fields = ["enrollment", "event_type"]
