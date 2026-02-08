import django_filters

from organization.models import (
    Organization,
    OrganizationRole,
    OrganizationMember,
    OrganizationInvite,
    OrganizationDomain,
)


class OrganizationFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(lookup_expr="iexact")
    org_type = django_filters.CharFilter(lookup_expr="iexact")
    active = django_filters.BooleanFilter()

    class Meta:
        model = Organization
        fields = ["code", "org_type", "active"]


class OrganizationRoleFilter(django_filters.FilterSet):
    organization = django_filters.UUIDFilter(field_name="organization_id")
    slug = django_filters.CharFilter(lookup_expr="iexact")
    is_default = django_filters.BooleanFilter()

    class Meta:
        model = OrganizationRole
        fields = ["organization", "slug", "is_default"]


class OrganizationMemberFilter(django_filters.FilterSet):
    organization = django_filters.UUIDFilter(field_name="organization_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    role = django_filters.UUIDFilter(field_name="role_id")
    status = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = OrganizationMember
        fields = ["organization", "user", "role", "status"]


class OrganizationInviteFilter(django_filters.FilterSet):
    organization = django_filters.UUIDFilter(field_name="organization_id")
    email = django_filters.CharFilter(lookup_expr="iexact")
    role = django_filters.UUIDFilter(field_name="role_id")
    status = django_filters.CharFilter(lookup_expr="iexact")
    token = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = OrganizationInvite
        fields = ["organization", "email", "role", "status", "token"]


class OrganizationDomainFilter(django_filters.FilterSet):
    organization = django_filters.UUIDFilter(field_name="organization_id")
    domain = django_filters.CharFilter(lookup_expr="iexact")
    is_primary = django_filters.BooleanFilter()
    is_verified = django_filters.BooleanFilter()

    class Meta:
        model = OrganizationDomain
        fields = ["organization", "domain", "is_primary", "is_verified"]
