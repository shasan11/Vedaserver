from core.utils.BulkModelViewSet import BaseModelViewSet
from content.models import (
    CourseModule,
    Lesson,
    LessonResource,
    LessonInstructorNote,
)
from content.serializers import (
    CourseModuleSerializer,
    LessonSerializer,
    LessonResourceSerializer,
    LessonInstructorNoteSerializer,
)
from content.filters import (
    CourseModuleFilter,
    LessonFilter,
    LessonResourceFilter,
    LessonInstructorNoteFilter,
)


class CourseModuleViewSet(BaseModelViewSet):
    queryset = CourseModule.objects.all()
    serializer_class = CourseModuleSerializer
    filterset_class = CourseModuleFilter
    search_fields = ["title", "description"]
    ordering_fields = "__all__"


class LessonViewSet(BaseModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    filterset_class = LessonFilter
    search_fields = ["title", "slug", "summary"]
    ordering_fields = "__all__"


class LessonResourceViewSet(BaseModelViewSet):
    queryset = LessonResource.objects.all()
    serializer_class = LessonResourceSerializer
    filterset_class = LessonResourceFilter
    search_fields = ["title", "description"]
    ordering_fields = "__all__"


class LessonInstructorNoteViewSet(BaseModelViewSet):
    queryset = LessonInstructorNote.objects.all()
    serializer_class = LessonInstructorNoteSerializer
    filterset_class = LessonInstructorNoteFilter
    search_fields = ["note"]
    ordering_fields = "__all__"
