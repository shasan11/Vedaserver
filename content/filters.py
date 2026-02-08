import django_filters

from content.models import (
    CourseModule,
    Lesson,
    LessonResource,
    LessonInstructorNote,
)


class CourseModuleFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    course = django_filters.UUIDFilter(field_name="course_id")
    visibility = django_filters.CharFilter(lookup_expr="iexact")
    release_type = django_filters.CharFilter(lookup_expr="iexact")
    active = django_filters.BooleanFilter()

    class Meta:
        model = CourseModule
        fields = ["branch", "course", "visibility", "release_type", "active"]


class LessonFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    course = django_filters.UUIDFilter(field_name="course_id")
    module = django_filters.UUIDFilter(field_name="module_id")
    lesson_type = django_filters.CharFilter(lookup_expr="iexact")
    status = django_filters.CharFilter(lookup_expr="iexact")
    slug = django_filters.CharFilter(lookup_expr="iexact")
    release_type = django_filters.CharFilter(lookup_expr="iexact")
    active = django_filters.BooleanFilter()

    class Meta:
        model = Lesson
        fields = ["branch", "course", "module", "lesson_type", "status", "slug", "release_type", "active"]


class LessonResourceFilter(django_filters.FilterSet):
    lesson = django_filters.UUIDFilter(field_name="lesson_id")
    resource_type = django_filters.CharFilter(lookup_expr="iexact")
    is_downloadable = django_filters.BooleanFilter()

    class Meta:
        model = LessonResource
        fields = ["lesson", "resource_type", "is_downloadable"]


class LessonInstructorNoteFilter(django_filters.FilterSet):
    lesson = django_filters.UUIDFilter(field_name="lesson_id")

    class Meta:
        model = LessonInstructorNote
        fields = ["lesson"]
