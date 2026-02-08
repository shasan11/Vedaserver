from core.utils.BulkModelViewSet import BaseModelViewSet
from organization.models import (
    Organization,
    OrganizationRole,
    OrganizationMember,
    OrganizationInvite,
    OrganizationDomain,
)
from organization.serializers import (
    OrganizationSerializer,
    OrganizationRoleSerializer,
    OrganizationMemberSerializer,
    OrganizationInviteSerializer,
    OrganizationDomainSerializer,
)
from organization.filters import (
    OrganizationFilter,
    OrganizationRoleFilter,
    OrganizationMemberFilter,
    OrganizationInviteFilter,
    OrganizationDomainFilter,
)


class OrganizationViewSet(BaseModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    filterset_class = OrganizationFilter
    search_fields = ["name", "legal_name", "code", "email", "phone"]
    ordering_fields = "__all__"


class OrganizationRoleViewSet(BaseModelViewSet):
    queryset = OrganizationRole.objects.all()
    serializer_class = OrganizationRoleSerializer
    filterset_class = OrganizationRoleFilter
    search_fields = ["slug", "name", "description"]
    ordering_fields = "__all__"


class OrganizationMemberViewSet(BaseModelViewSet):
    queryset = OrganizationMember.objects.all()
    serializer_class = OrganizationMemberSerializer
    filterset_class = OrganizationMemberFilter
    search_fields = ["user__email", "organization__name"]
    ordering_fields = "__all__"


class OrganizationInviteViewSet(BaseModelViewSet):
    queryset = OrganizationInvite.objects.all()
    serializer_class = OrganizationInviteSerializer
    filterset_class = OrganizationInviteFilter
    search_fields = ["email", "token"]
    ordering_fields = "__all__"


class OrganizationDomainViewSet(BaseModelViewSet):
    queryset = OrganizationDomain.objects.all()
    serializer_class = OrganizationDomainSerializer
    filterset_class = OrganizationDomainFilter
    search_fields = ["domain"]
    ordering_fields = "__all__"
