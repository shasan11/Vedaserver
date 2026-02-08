from django.urls import path, include
from rest_framework_bulk.routes import BulkRouter

from courses.views import (
    CourseCategoryViewSet,
    CourseTagViewSet,
    CourseViewSet,
    CourseTaggingViewSet,
    CourseInstructorViewSet,
    CoursePricingViewSet,
    CourseOutcomeViewSet,
    CourseRequirementViewSet,
    CourseTargetAudienceViewSet,
    CourseFAQViewSet,
    CourseReviewViewSet,
)

router = BulkRouter()
router.register(r"course-categories", CourseCategoryViewSet, basename="course-category")
router.register(r"course-tags", CourseTagViewSet, basename="course-tag")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"course-taggings", CourseTaggingViewSet, basename="course-tagging")
router.register(r"course-instructors", CourseInstructorViewSet, basename="course-instructor")
router.register(r"course-pricing", CoursePricingViewSet, basename="course-pricing")
router.register(r"course-outcomes", CourseOutcomeViewSet, basename="course-outcome")
router.register(r"course-requirements", CourseRequirementViewSet, basename="course-requirement")
router.register(r"course-target-audiences", CourseTargetAudienceViewSet, basename="course-target-audience")
router.register(r"course-faqs", CourseFAQViewSet, basename="course-faq")
router.register(r"course-reviews", CourseReviewViewSet, basename="course-review")

urlpatterns = [
    path("", include(router.urls)),
]
