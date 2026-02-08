# settings/filters.py
import django_filters

from settings.models import (
    Currency, Country, Language,
    Organization, Branch,
    OrganizationSettings, BranchSettings,
    FeatureFlag, NumberSequence, BranchMembership
)


class CurrencyFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(lookup_expr="iexact")
    name = django_filters.CharFilter(lookup_expr="icontains")
    active = django_filters.BooleanFilter()

    class Meta:
        model = Currency
        fields = ["code", "name", "active"]


class CountryFilter(django_filters.FilterSet):
    iso2 = django_filters.CharFilter(lookup_expr="iexact")
    name = django_filters.CharFilter(lookup_expr="icontains")
    active = django_filters.BooleanFilter()

    class Meta:
        model = Country
        fields = ["iso2", "name", "active"]


class LanguageFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(lookup_expr="iexact")
    name = django_filters.CharFilter(lookup_expr="icontains")
    active = django_filters.BooleanFilter()
    is_rtl = django_filters.BooleanFilter()

    class Meta:
        model = Language
        fields = ["code", "name", "active", "is_rtl"]


class OrganizationFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(lookup_expr="iexact")
    name = django_filters.CharFilter(lookup_expr="icontains")
    org_type = django_filters.CharFilter(lookup_expr="iexact")
    country = django_filters.UUIDFilter(field_name="country_id")
    active = django_filters.BooleanFilter()

    class Meta:
        model = Organization
        fields = ["code", "name", "org_type", "country", "active"]


class BranchFilter(django_filters.FilterSet):
    organization = django_filters.UUIDFilter(field_name="organization_id")
    code = django_filters.CharFilter(lookup_expr="iexact")
    name = django_filters.CharFilter(lookup_expr="icontains")
    branch_type = django_filters.CharFilter(lookup_expr="iexact")
    country = django_filters.UUIDFilter(field_name="country_id")
    active = django_filters.BooleanFilter()
    is_default = django_filters.BooleanFilter()

    class Meta:
        model = Branch
        fields = ["organization", "code", "name", "branch_type", "country", "active", "is_default"]


class OrganizationSettingsFilter(django_filters.FilterSet):
    organization = django_filters.UUIDFilter(field_name="organization_id")

    class Meta:
        model = OrganizationSettings
        fields = ["organization"]


class BranchSettingsFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")

    class Meta:
        model = BranchSettings
        fields = ["branch"]


class FeatureFlagFilter(django_filters.FilterSet):
    key = django_filters.CharFilter(lookup_expr="icontains")
    scope = django_filters.CharFilter(lookup_expr="iexact")
    enabled = django_filters.BooleanFilter()
    organization = django_filters.UUIDFilter(field_name="organization_id")
    branch = django_filters.UUIDFilter(field_name="branch_id")

    class Meta:
        model = FeatureFlag
        fields = ["key", "scope", "enabled", "organization", "branch"]


class NumberSequenceFilter(django_filters.FilterSet):
    seq_type = django_filters.CharFilter(lookup_expr="iexact")
    organization = django_filters.UUIDFilter(field_name="organization_id")
    branch = django_filters.UUIDFilter(field_name="branch_id")

    class Meta:
        model = NumberSequence
        fields = ["seq_type", "organization", "branch"]


class BranchMembershipFilter(django_filters.FilterSet):
    user = django_filters.UUIDFilter(field_name="user_id")
    branch = django_filters.UUIDFilter(field_name="branch_id")
    is_default = django_filters.BooleanFilter()
    role_hint = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = BranchMembership
        fields = ["user", "branch", "is_default", "role_hint"]
