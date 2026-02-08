from core.utils.AdaptedBulkSerializer import BulkModelSerializer
from progress.models import (
    CourseProgress,
    LessonProgress,
    DailyLearningTime,
    ProgressEvent,
)


class CourseProgressSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CourseProgress
        fields = "__all__"


class LessonProgressSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = LessonProgress
        fields = "__all__"


class DailyLearningTimeSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = DailyLearningTime
        fields = "__all__"


class ProgressEventSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = ProgressEvent
        fields = "__all__"
