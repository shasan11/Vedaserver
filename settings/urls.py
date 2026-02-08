# settings/urls.py
from django.urls import path, include
from rest_framework_bulk.routes import BulkRouter
from settings.views import (
    CurrencyViewSet, CountryViewSet, LanguageViewSet,
    OrganizationViewSet, BranchViewSet,
    OrganizationSettingsViewSet, BranchSettingsViewSet,
    FeatureFlagViewSet, NumberSequenceViewSet, BranchMembershipViewSet
)

router = BulkRouter()
router.register(r"currencies", CurrencyViewSet, basename="currency")
router.register(r"countries", CountryViewSet, basename="country")
router.register(r"languages", LanguageViewSet, basename="language")

router.register(r"organizations", OrganizationViewSet, basename="organization")
router.register(r"branches", BranchViewSet, basename="branch")

router.register(r"organization-settings", OrganizationSettingsViewSet, basename="organization-settings")
router.register(r"branch-settings", BranchSettingsViewSet, basename="branch-settings")

router.register(r"feature-flags", FeatureFlagViewSet, basename="feature-flag")
router.register(r"number-sequences", NumberSequenceViewSet, basename="number-sequence")
router.register(r"branch-memberships", BranchMembershipViewSet, basename="branch-membership")

urlpatterns = [
    path("", include(router.urls)),
]
