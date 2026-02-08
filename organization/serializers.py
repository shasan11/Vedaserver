from core.utils.AdaptedBulkSerializer import BulkModelSerializer
from organization.models import (
    Organization,
    OrganizationRole,
    OrganizationMember,
    OrganizationInvite,
    OrganizationDomain,
)


class OrganizationSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Organization
        fields = "__all__"


class OrganizationRoleSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = OrganizationRole
        fields = "__all__"


class OrganizationMemberSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = OrganizationMember
        fields = "__all__"


class OrganizationInviteSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = OrganizationInvite
        fields = "__all__"


class OrganizationDomainSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = OrganizationDomain
        fields = "__all__"
