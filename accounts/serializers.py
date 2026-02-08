from core.utils.AdaptedBulkSerializer import BulkModelSerializer
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


class UserSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = User
        fields = "__all__"


class UserProfileSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = UserProfile
        fields = "__all__"


class StudentProfileSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = StudentProfile
        fields = "__all__"


class InstructorProfileSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = InstructorProfile
        fields = "__all__"


class RoleSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Role
        fields = "__all__"


class UserRoleSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = UserRole
        fields = "__all__"


class UserTokenSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = UserToken
        fields = "__all__"


class LoginAuditSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = LoginAudit
        fields = "__all__"
