import django_filters

from progress.models import (
    CourseProgress,
    LessonProgress,
    DailyLearningTime,
    ProgressEvent,
)


class CourseProgressFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    course = django_filters.UUIDFilter(field_name="course_id")
    enrollment = django_filters.UUIDFilter(field_name="enrollment_id")
    status = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = CourseProgress
        fields = ["branch", "user", "course", "enrollment", "status"]


class LessonProgressFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    course = django_filters.UUIDFilter(field_name="course_id")
    lesson = django_filters.UUIDFilter(field_name="lesson_id")
    enrollment = django_filters.UUIDFilter(field_name="enrollment_id")
    status = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = LessonProgress
        fields = ["branch", "user", "course", "lesson", "enrollment", "status"]


class DailyLearningTimeFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    course = django_filters.UUIDFilter(field_name="course_id")
    date = django_filters.DateFilter()

    class Meta:
        model = DailyLearningTime
        fields = ["branch", "user", "course", "date"]


class ProgressEventFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    course = django_filters.UUIDFilter(field_name="course_id")
    lesson = django_filters.UUIDFilter(field_name="lesson_id")
    event_type = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = ProgressEvent
        fields = ["branch", "user", "course", "lesson", "event_type"]
