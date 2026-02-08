from django.urls import path, include
from rest_framework_bulk.routes import BulkRouter

from content.views import (
    CourseModuleViewSet,
    LessonViewSet,
    LessonResourceViewSet,
    LessonInstructorNoteViewSet,
)

router = BulkRouter()
router.register(r"course-modules", CourseModuleViewSet, basename="course-module")
router.register(r"lessons", LessonViewSet, basename="lesson")
router.register(r"lesson-resources", LessonResourceViewSet, basename="lesson-resource")
router.register(r"lesson-instructor-notes", LessonInstructorNoteViewSet, basename="lesson-instructor-note")

urlpatterns = [
    path("", include(router.urls)),
]
