
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_bulk.generics import BulkModelViewSet
from settings.models import Branch
from core.utils.IsMainBranchOrOwnBranch import IsMainBranchOrOwnBranch
from core.utils.userSession import get_current_user_branch

class IsAuthenticated(permissions.IsAuthenticated):
    pass

class BranchScopedMixin:
    """
    Scope queryset by user's branch unless the user belongs to the main branch.
    """

    def get_queryset(self):
        qs = super().get_queryset()

        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return qs.none()  # or just return qs if you want anonymous to see nothing

        # If model has a branch field
        model_cls = self.serializer_class.Meta.model
        if any(f.name == "branch" for f in model_cls._meta.get_fields()):
            branch = getattr(user, "branch", None)
            if branch:
                if getattr(branch, "is_main_branch", False):
                    # Main branch → see everything
                    return qs
                else:
                    # Non-main branch → filter only own branch
                    return qs.filter(branch=branch)

        # If no branch field, just return all
        return qs


class BaseModelViewSet(BranchScopedMixin, BulkModelViewSet):
    permission_classes = [IsAuthenticated, IsMainBranchOrOwnBranch]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = "__all__"
    search_fields = []
    filterset_class = None

    def _model_has_field(self, model_cls, field_name: str) -> bool:
        return any(getattr(f, "name", None) == field_name for f in model_cls._meta.get_fields())

    def _valid_branch_for(self, user):
        """Return a valid Branch object for this user, else None."""
        branch = getattr(user, "branch", None)
        if branch and Branch.objects.filter(pk=branch.pk).exists():
            return branch

        # Optional fallback from session helper
        try:
            fb_id = get_current_user_branch()
        except Exception:
            fb_id = None
        if fb_id and Branch.objects.filter(pk=fb_id).exists():
            return Branch.objects.get(pk=fb_id)

        return None

    def perform_create(self, serializer):
        model_cls = serializer.Meta.model
        branch = self._valid_branch_for(self.request.user)
        extra = {}
        if branch and self._model_has_field(model_cls, "branch"):
            extra["branch"] = branch
        serializer.save(**extra)

    def perform_update(self, serializer):
        model_cls = serializer.Meta.model
        branch = self._valid_branch_for(self.request.user)
        extra = {}
        if branch and self._model_has_field(model_cls, "branch"):
            extra["branch"] = branch
        serializer.save(**extra)

