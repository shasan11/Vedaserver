from django.urls import path, include
from rest_framework_bulk.routes import BulkRouter

from progress.views import (
    CourseProgressViewSet,
    LessonProgressViewSet,
    DailyLearningTimeViewSet,
    ProgressEventViewSet,
)

router = BulkRouter()
router.register(r"course-progress", CourseProgressViewSet, basename="course-progress")
router.register(r"lesson-progress", LessonProgressViewSet, basename="lesson-progress")
router.register(r"daily-learning-time", DailyLearningTimeViewSet, basename="daily-learning-time")
router.register(r"progress-events", ProgressEventViewSet, basename="progress-event")

urlpatterns = [
    path("", include(router.urls)),
]
