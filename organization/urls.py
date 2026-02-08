from django.urls import path, include
from rest_framework_bulk.routes import BulkRouter

from organization.views import (
    OrganizationViewSet,
    OrganizationRoleViewSet,
    OrganizationMemberViewSet,
    OrganizationInviteViewSet,
    OrganizationDomainViewSet,
)

router = BulkRouter()
router.register(r"organizations", OrganizationViewSet, basename="organization")
router.register(r"organization-roles", OrganizationRoleViewSet, basename="organization-role")
router.register(r"organization-members", OrganizationMemberViewSet, basename="organization-member")
router.register(r"organization-invites", OrganizationInviteViewSet, basename="organization-invite")
router.register(r"organization-domains", OrganizationDomainViewSet, basename="organization-domain")

urlpatterns = [
    path("", include(router.urls)),
]
