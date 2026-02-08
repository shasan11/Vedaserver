from core.utils.BulkModelViewSet import BaseModelViewSet
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
from accounts.serializers import (
    UserSerializer,
    UserProfileSerializer,
    StudentProfileSerializer,
    InstructorProfileSerializer,
    RoleSerializer,
    UserRoleSerializer,
    UserTokenSerializer,
    LoginAuditSerializer,
)
from accounts.filters import (
    UserFilter,
    UserProfileFilter,
    StudentProfileFilter,
    InstructorProfileFilter,
    RoleFilter,
    UserRoleFilter,
    UserTokenFilter,
    LoginAuditFilter,
)


class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter
    search_fields = ["email", "first_name", "last_name", "phone"]
    ordering_fields = "__all__"


class UserProfileViewSet(BaseModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    filterset_class = UserProfileFilter
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    ordering_fields = "__all__"


class StudentProfileViewSet(BaseModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    filterset_class = StudentProfileFilter
    search_fields = ["user__email", "guardian_name", "guardian_phone", "institute"]
    ordering_fields = "__all__"


class InstructorProfileViewSet(BaseModelViewSet):
    queryset = InstructorProfile.objects.all()
    serializer_class = InstructorProfileSerializer
    filterset_class = InstructorProfileFilter
    search_fields = ["user__email", "headline"]
    ordering_fields = "__all__"


class RoleViewSet(BaseModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filterset_class = RoleFilter
    search_fields = ["name", "slug"]
    ordering_fields = "__all__"


class UserRoleViewSet(BaseModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    filterset_class = UserRoleFilter
    search_fields = ["user__email", "role__slug", "role__name"]
    ordering_fields = "__all__"


class UserTokenViewSet(BaseModelViewSet):
    queryset = UserToken.objects.all()
    serializer_class = UserTokenSerializer
    filterset_class = UserTokenFilter
    search_fields = ["token", "purpose", "user__email"]
    ordering_fields = "__all__"


class LoginAuditViewSet(BaseModelViewSet):
    queryset = LoginAudit.objects.all()
    serializer_class = LoginAuditSerializer
    filterset_class = LoginAuditFilter
    search_fields = ["email_entered", "ip_address", "user__email"]
    ordering_fields = "__all__"
