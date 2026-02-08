from core.utils.AdaptedBulkSerializer import BulkModelSerializer
from content.models import (
    CourseModule,
    Lesson,
    LessonResource,
    LessonInstructorNote,
)


class CourseModuleSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CourseModule
        fields = "__all__"


class LessonSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Lesson
        fields = "__all__"


class LessonResourceSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = LessonResource
        fields = "__all__"


class LessonInstructorNoteSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = LessonInstructorNote
        fields = "__all__"
