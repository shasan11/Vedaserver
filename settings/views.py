# settings/views.py
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response

from core.utils.BulkModelViewSet import BaseModelViewSet
from settings.models import (
    Currency, Country, Language,
    Organization, Branch,
    OrganizationSettings, BranchSettings,
    FeatureFlag, NumberSequence, BranchMembership
)
from settings.serializers import (
    CurrencySerializer, CountrySerializer, LanguageSerializer,
    OrganizationSerializer, BranchSerializer,
    OrganizationSettingsSerializer, BranchSettingsSerializer,
    FeatureFlagSerializer, NumberSequenceSerializer, BranchMembershipSerializer
)
from settings.filters import (
    CurrencyFilter, CountryFilter, LanguageFilter,
    OrganizationFilter, BranchFilter,
    OrganizationSettingsFilter, BranchSettingsFilter,
    FeatureFlagFilter, NumberSequenceFilter, BranchMembershipFilter
)


class SettingsBaseModelViewSet(BaseModelViewSet):
    """
    Fixes BaseModelViewSet bug:
    - Your BaseModelViewSet.perform_create() always injects branch, which crashes for models without branch field.
    - Also prevents corrupting branch/org on update for main-branch users.
    """

    def _user_branch(self):
        return getattr(self.request.user, "branch", None)

    def _is_main_branch(self, branch):
        return bool(getattr(branch, "is_main_branch", False))

    def _user_org(self):
        br = self._user_branch()
        return getattr(br, "organization", None) if br else None

    def _model_has_field(self, model_cls, field_name: str) -> bool:
        return any(getattr(f, "name", None) == field_name for f in model_cls._meta.get_fields())

    def perform_create(self, serializer):
        model_cls = serializer.Meta.model
        user_branch = self._user_branch()
        user_org = self._user_org()

        extra = {}

        # Branch injection ONLY if model has 'branch'
        if self._model_has_field(model_cls, "branch") and user_branch:
            if not self._is_main_branch(user_branch):
                # Non-main branch users: force own branch
                extra["branch"] = user_branch
            else:
                # Main branch: set default branch only if not provided
                if "branch" not in serializer.validated_data:
                    extra["branch"] = user_branch

        # Org injection ONLY if model has 'organization' (and isn't Organization itself)
        if model_cls is not Organization and self._model_has_field(model_cls, "organization") and user_org:
            if not self._is_main_branch(user_branch):
                extra["organization"] = user_org
            else:
                if "organization" not in serializer.validated_data:
                    extra["organization"] = user_org

        serializer.save(**extra)

    def perform_update(self, serializer):
        model_cls = serializer.Meta.model
        user_branch = self._user_branch()
        user_org = self._user_org()

        extra = {}

        # On update: only FORCE branch/org for non-main users; do not auto-overwrite for main users
        if self._model_has_field(model_cls, "branch") and user_branch and not self._is_main_branch(user_branch):
            extra["branch"] = user_branch

        if model_cls is not Organization and self._model_has_field(model_cls, "organization") and user_org and not self._is_main_branch(user_branch):
            extra["organization"] = user_org

        serializer.save(**extra)


# ----------------------------- Reference Masters -----------------------------

class CurrencyViewSet(SettingsBaseModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    filterset_class = CurrencyFilter
    search_fields = ["code", "name", "symbol"]
    ordering_fields = "__all__"


class CountryViewSet(SettingsBaseModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filterset_class = CountryFilter
    search_fields = ["iso2", "name", "phone_code"]
    ordering_fields = "__all__"


class LanguageViewSet(SettingsBaseModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    filterset_class = LanguageFilter
    search_fields = ["code", "name"]
    ordering_fields = "__all__"


# ----------------------------- Organization / Branch -----------------------------

class OrganizationViewSet(SettingsBaseModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    filterset_class = OrganizationFilter
    search_fields = ["name", "legal_name", "code", "email", "phone"]
    ordering_fields = "__all__"

    def get_queryset(self):
        qs = super().get_queryset()
        br = self._user_branch()
        if br and not self._is_main_branch(br):
            org = getattr(br, "organization", None)
            if org:
                return qs.filter(id=org.id)
            return qs.none()
        return qs

    @action(detail=False, methods=["get"])
    def me(self, request):
        br = self._user_branch()
        if not br:
            return Response({"detail": "User has no branch."}, status=400)
        org = getattr(br, "organization", None)
        if not org:
            return Response({"detail": "User branch has no organization."}, status=400)
        return Response(self.get_serializer(org).data)


class BranchViewSet(SettingsBaseModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    filterset_class = BranchFilter
    search_fields = ["name", "code", "email", "phone"]
    ordering_fields = "__all__"

    def get_queryset(self):
        qs = super().get_queryset()
        br = self._user_branch()
        if br and not self._is_main_branch(br):
            return qs.filter(id=br.id)
        return qs

    @action(detail=False, methods=["get"])
    def me(self, request):
        br = self._user_branch()
        if not br:
            return Response({"detail": "User has no branch."}, status=400)
        return Response(self.get_serializer(br).data)


# ----------------------------- Settings Containers -----------------------------

class OrganizationSettingsViewSet(SettingsBaseModelViewSet):
    queryset = OrganizationSettings.objects.all()
    serializer_class = OrganizationSettingsSerializer
    filterset_class = OrganizationSettingsFilter
    search_fields = []
    ordering_fields = "__all__"

    def get_queryset(self):
        qs = super().get_queryset()
        br = self._user_branch()
        if br and not self._is_main_branch(br):
            org = getattr(br, "organization", None)
            if org:
                return qs.filter(organization=org)
            return qs.none()
        return qs

    @action(detail=False, methods=["get"])
    def my(self, request):
        br = self._user_branch()
        org = getattr(br, "organization", None) if br else None
        if not org:
            return Response({"detail": "No organization found for user."}, status=400)
        obj, _ = OrganizationSettings.objects.get_or_create(organization=org)
        return Response(self.get_serializer(obj).data)


class BranchSettingsViewSet(SettingsBaseModelViewSet):
    queryset = BranchSettings.objects.all()
    serializer_class = BranchSettingsSerializer
    filterset_class = BranchSettingsFilter
    search_fields = []
    ordering_fields = "__all__"

    def get_queryset(self):
        qs = super().get_queryset()
        br = self._user_branch()
        if br and not self._is_main_branch(br):
            return qs.filter(branch=br)
        return qs

    @action(detail=False, methods=["get"])
    def my(self, request):
        br = self._user_branch()
        if not br:
            return Response({"detail": "User has no branch."}, status=400)
        obj, _ = BranchSettings.objects.get_or_create(branch=br)
        return Response(self.get_serializer(obj).data)


# ----------------------------- Feature Flags -----------------------------

class FeatureFlagViewSet(SettingsBaseModelViewSet):
    queryset = FeatureFlag.objects.all()
    serializer_class = FeatureFlagSerializer
    filterset_class = FeatureFlagFilter
    search_fields = ["key", "description"]
    ordering_fields = "__all__"

    def get_queryset(self):
        qs = super().get_queryset()
        br = self._user_branch()
        if br and not self._is_main_branch(br):
            org = getattr(br, "organization", None)
            # Non-main: see global + org + branch scoped flags
            return qs.filter(
                Q(scope="global", organization__isnull=True, branch__isnull=True) |
                Q(organization=org) |
                Q(branch=br)
            ).distinct()
        return qs


# ----------------------------- Numbering / Sequences -----------------------------

class NumberSequenceViewSet(SettingsBaseModelViewSet):
    queryset = NumberSequence.objects.all()
    serializer_class = NumberSequenceSerializer
    filterset_class = NumberSequenceFilter
    search_fields = ["seq_type", "prefix"]
    ordering_fields = "__all__"

    def get_queryset(self):
        qs = super().get_queryset()
        br = self._user_branch()
        if br and not self._is_main_branch(br):
            org = getattr(br, "organization", None)
            # Non-main: see sequences within org and/or their branch
            return qs.filter(Q(organization=org) | Q(branch=br)).distinct()
        return qs

    @action(detail=True, methods=["get"])
    def peek(self, request, pk=None):
        obj = self.get_object()
        return Response({"value": obj.peek()})

    @action(detail=True, methods=["post"])
    def consume(self, request, pk=None):
        obj = self.get_object()
        value = obj.consume(save=True)
        return Response({"value": value})


# ----------------------------- Branch Membership -----------------------------

class BranchMembershipViewSet(SettingsBaseModelViewSet):
    queryset = BranchMembership.objects.all()
    serializer_class = BranchMembershipSerializer
    filterset_class = BranchMembershipFilter
    search_fields = ["role_hint", "user__username", "user__email"]
    ordering_fields = "__all__"

    def get_queryset(self):
        qs = super().get_queryset()
        br = self._user_branch()
        if br and not self._is_main_branch(br):
            return qs.filter(branch=br)
        return qs
