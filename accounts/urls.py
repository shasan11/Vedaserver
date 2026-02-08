from django.urls import path, include
from rest_framework_bulk.routes import BulkRouter

from accounts.views import (
    UserViewSet,
    UserProfileViewSet,
    StudentProfileViewSet,
    InstructorProfileViewSet,
    RoleViewSet,
    UserRoleViewSet,
    UserTokenViewSet,
    LoginAuditViewSet,
)

router = BulkRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"user-profiles", UserProfileViewSet, basename="user-profile")
router.register(r"student-profiles", StudentProfileViewSet, basename="student-profile")
router.register(r"instructor-profiles", InstructorProfileViewSet, basename="instructor-profile")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"user-roles", UserRoleViewSet, basename="user-role")
router.register(r"user-tokens", UserTokenViewSet, basename="user-token")
router.register(r"login-audits", LoginAuditViewSet, basename="login-audit")

urlpatterns = [
    path("", include(router.urls)),
]
