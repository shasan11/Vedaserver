from core.utils.BulkModelViewSet import BaseModelViewSet
from enrollments.models import (
    CourseCohort,
    Enrollment,
    EnrollmentAccessOverride,
    CourseAccessInvite,
    EnrollmentEvent,
)
from enrollments.serializers import (
    CourseCohortSerializer,
    EnrollmentSerializer,
    EnrollmentAccessOverrideSerializer,
    CourseAccessInviteSerializer,
    EnrollmentEventSerializer,
)
from enrollments.filters import (
    CourseCohortFilter,
    EnrollmentFilter,
    EnrollmentAccessOverrideFilter,
    CourseAccessInviteFilter,
    EnrollmentEventFilter,
)


class CourseCohortViewSet(BaseModelViewSet):
    queryset = CourseCohort.objects.all()
    serializer_class = CourseCohortSerializer
    filterset_class = CourseCohortFilter
    search_fields = ["name", "code", "notes"]
    ordering_fields = "__all__"


class EnrollmentViewSet(BaseModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    filterset_class = EnrollmentFilter
    search_fields = ["billing_order_ref", "cancel_reason", "suspended_reason"]
    ordering_fields = "__all__"


class EnrollmentAccessOverrideViewSet(BaseModelViewSet):
    queryset = EnrollmentAccessOverride.objects.all()
    serializer_class = EnrollmentAccessOverrideSerializer
    filterset_class = EnrollmentAccessOverrideFilter
    search_fields = ["note"]
    ordering_fields = "__all__"


class CourseAccessInviteViewSet(BaseModelViewSet):
    queryset = CourseAccessInvite.objects.all()
    serializer_class = CourseAccessInviteSerializer
    filterset_class = CourseAccessInviteFilter
    search_fields = ["email", "token"]
    ordering_fields = "__all__"


class EnrollmentEventViewSet(BaseModelViewSet):
    queryset = EnrollmentEvent.objects.all()
    serializer_class = EnrollmentEventSerializer
    filterset_class = EnrollmentEventFilter
    search_fields = ["event_type", "message"]
    ordering_fields = "__all__"
