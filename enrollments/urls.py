from django.urls import path, include
from rest_framework_bulk.routes import BulkRouter

from enrollments.views import (
    CourseCohortViewSet,
    EnrollmentViewSet,
    EnrollmentAccessOverrideViewSet,
    CourseAccessInviteViewSet,
    EnrollmentEventViewSet,
)

router = BulkRouter()
router.register(r"course-cohorts", CourseCohortViewSet, basename="course-cohort")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")
router.register(r"enrollment-access-overrides", EnrollmentAccessOverrideViewSet, basename="enrollment-access-override")
router.register(r"course-access-invites", CourseAccessInviteViewSet, basename="course-access-invite")
router.register(r"enrollment-events", EnrollmentEventViewSet, basename="enrollment-event")

urlpatterns = [
    path("", include(router.urls)),
]
