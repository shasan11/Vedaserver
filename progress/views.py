from core.utils.BulkModelViewSet import BaseModelViewSet
from progress.models import (
    CourseProgress,
    LessonProgress,
    DailyLearningTime,
    ProgressEvent,
)
from progress.serializers import (
    CourseProgressSerializer,
    LessonProgressSerializer,
    DailyLearningTimeSerializer,
    ProgressEventSerializer,
)
from progress.filters import (
    CourseProgressFilter,
    LessonProgressFilter,
    DailyLearningTimeFilter,
    ProgressEventFilter,
)


class CourseProgressViewSet(BaseModelViewSet):
    queryset = CourseProgress.objects.all()
    serializer_class = CourseProgressSerializer
    filterset_class = CourseProgressFilter
    search_fields = ["status"]
    ordering_fields = "__all__"


class LessonProgressViewSet(BaseModelViewSet):
    queryset = LessonProgress.objects.all()
    serializer_class = LessonProgressSerializer
    filterset_class = LessonProgressFilter
    search_fields = ["status"]
    ordering_fields = "__all__"


class DailyLearningTimeViewSet(BaseModelViewSet):
    queryset = DailyLearningTime.objects.all()
    serializer_class = DailyLearningTimeSerializer
    filterset_class = DailyLearningTimeFilter
    search_fields = []
    ordering_fields = "__all__"


class ProgressEventViewSet(BaseModelViewSet):
    queryset = ProgressEvent.objects.all()
    serializer_class = ProgressEventSerializer
    filterset_class = ProgressEventFilter
    search_fields = ["event_type"]
    ordering_fields = "__all__"
