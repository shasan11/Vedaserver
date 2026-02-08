from core.utils.AdaptedBulkSerializer import BulkModelSerializer
from enrollments.models import (
    CourseCohort,
    Enrollment,
    EnrollmentAccessOverride,
    CourseAccessInvite,
    EnrollmentEvent,
)


class CourseCohortSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CourseCohort
        fields = "__all__"


class EnrollmentSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Enrollment
        fields = "__all__"


class EnrollmentAccessOverrideSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = EnrollmentAccessOverride
        fields = "__all__"


class CourseAccessInviteSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CourseAccessInvite
        fields = "__all__"


class EnrollmentEventSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = EnrollmentEvent
        fields = "__all__"
