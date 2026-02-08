# settings/serializers.py
from rest_framework import serializers

from core.utils.AdaptedBulkSerializer import BulkModelSerializer
from settings.models import (
    Currency, Country, Language,
    Organization, Branch,
    OrganizationSettings, BranchSettings,
    FeatureFlag, NumberSequence, BranchMembership
)


class CurrencySerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Currency
        fields = "__all__"

    def validate_code(self, value):
        value = (value or "").upper().strip()
        if len(value) != 3:
            raise serializers.ValidationError("Currency code must be exactly 3 characters (e.g., NPR, USD).")
        return value


class CountrySerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Country
        fields = "__all__"

    def validate_iso2(self, value):
        value = (value or "").upper().strip()
        if len(value) != 2:
            raise serializers.ValidationError("Country iso2 must be exactly 2 characters (e.g., NP, AE).")
        return value


class LanguageSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Language
        fields = "__all__"

    def validate_code(self, value):
        value = (value or "").lower().strip()
        if len(value) < 2:
            raise serializers.ValidationError("Language code looks too short (e.g., en, ne).")
        return value


class OrganizationSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Organization
        fields = "__all__"


class BranchSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Branch
        fields = "__all__"


class OrganizationSettingsSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = OrganizationSettings
        fields = "__all__"


class BranchSettingsSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = BranchSettings
        fields = "__all__"


class FeatureFlagSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = FeatureFlag
        fields = "__all__"


class NumberSequenceSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = NumberSequence
        fields = "__all__"


class BranchMembershipSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = BranchMembership
        fields = "__all__"
