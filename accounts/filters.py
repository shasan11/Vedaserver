import django_filters

from accounts.models import (
    User,
    UserProfile,
    StudentProfile,
    InstructorProfile,
    Role,
    UserRole,
    UserToken,
    LoginAudit,
)


class UserFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(lookup_expr="iexact")
    phone = django_filters.CharFilter(lookup_expr="iexact")
    user_type = django_filters.CharFilter(lookup_expr="iexact")
    is_active = django_filters.BooleanFilter()
    is_staff = django_filters.BooleanFilter()

    class Meta:
        model = User
        fields = ["email", "phone", "user_type", "is_active", "is_staff"]


class UserProfileFilter(django_filters.FilterSet):
    user = django_filters.UUIDFilter(field_name="user_id")
    gender = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = UserProfile
        fields = ["user", "gender"]


class StudentProfileFilter(django_filters.FilterSet):
    user = django_filters.UUIDFilter(field_name="user_id")
    level = django_filters.CharFilter(lookup_expr="icontains")
    institute = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = StudentProfile
        fields = ["user", "level", "institute"]


class InstructorProfileFilter(django_filters.FilterSet):
    user = django_filters.UUIDFilter(field_name="user_id")
    is_verified = django_filters.BooleanFilter()

    class Meta:
        model = InstructorProfile
        fields = ["user", "is_verified"]


class RoleFilter(django_filters.FilterSet):
    slug = django_filters.CharFilter(lookup_expr="iexact")
    is_default = django_filters.BooleanFilter()

    class Meta:
        model = Role
        fields = ["slug", "is_default"]


class UserRoleFilter(django_filters.FilterSet):
    user = django_filters.UUIDFilter(field_name="user_id")
    role = django_filters.UUIDFilter(field_name="role_id")

    class Meta:
        model = UserRole
        fields = ["user", "role"]


class UserTokenFilter(django_filters.FilterSet):
    user = django_filters.UUIDFilter(field_name="user_id")
    purpose = django_filters.CharFilter(lookup_expr="iexact")
    token = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = UserToken
        fields = ["user", "purpose", "token"]


class LoginAuditFilter(django_filters.FilterSet):
    user = django_filters.UUIDFilter(field_name="user_id")
    success = django_filters.BooleanFilter()
    email_entered = django_filters.CharFilter(lookup_expr="iexact")
    ip_address = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = LoginAudit
        fields = ["user", "success", "email_entered", "ip_address"]
