from core.utils.BulkModelViewSet import BaseModelViewSet
from assessments.models import (
    QuestionCategory,
    QuestionTag,
    QuestionBank,
    Question,
    QuestionOption,
    Quiz,
    QuizQuestion,
    QuizAttempt,
    AttemptAnswer,
    Assignment,
    AssignmentSubmission,
)
from assessments.serializers import (
    QuestionCategorySerializer,
    QuestionTagSerializer,
    QuestionBankSerializer,
    QuestionSerializer,
    QuestionOptionSerializer,
    QuizSerializer,
    QuizQuestionSerializer,
    QuizAttemptSerializer,
    AttemptAnswerSerializer,
    AssignmentSerializer,
    AssignmentSubmissionSerializer,
)
from assessments.filters import (
    QuestionCategoryFilter,
    QuestionTagFilter,
    QuestionBankFilter,
    QuestionFilter,
    QuestionOptionFilter,
    QuizFilter,
    QuizQuestionFilter,
    QuizAttemptFilter,
    AttemptAnswerFilter,
    AssignmentFilter,
    AssignmentSubmissionFilter,
)


class QuestionCategoryViewSet(BaseModelViewSet):
    queryset = QuestionCategory.objects.all()
    serializer_class = QuestionCategorySerializer
    filterset_class = QuestionCategoryFilter
    search_fields = ["name", "slug"]
    ordering_fields = "__all__"


class QuestionTagViewSet(BaseModelViewSet):
    queryset = QuestionTag.objects.all()
    serializer_class = QuestionTagSerializer
    filterset_class = QuestionTagFilter
    search_fields = ["name", "slug"]
    ordering_fields = "__all__"


class QuestionBankViewSet(BaseModelViewSet):
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankSerializer
    filterset_class = QuestionBankFilter
    search_fields = ["name", "description"]
    ordering_fields = "__all__"


class QuestionViewSet(BaseModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filterset_class = QuestionFilter
    search_fields = ["title", "prompt", "question_type"]
    ordering_fields = "__all__"


class QuestionOptionViewSet(BaseModelViewSet):
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer
    filterset_class = QuestionOptionFilter
    search_fields = ["text"]
    ordering_fields = "__all__"


class QuizViewSet(BaseModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    filterset_class = QuizFilter
    search_fields = ["title", "slug", "description"]
    ordering_fields = "__all__"


class QuizQuestionViewSet(BaseModelViewSet):
    queryset = QuizQuestion.objects.all()
    serializer_class = QuizQuestionSerializer
    filterset_class = QuizQuestionFilter
    search_fields = []
    ordering_fields = "__all__"


class QuizAttemptViewSet(BaseModelViewSet):
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer
    filterset_class = QuizAttemptFilter
    search_fields = ["status"]
    ordering_fields = "__all__"


class AttemptAnswerViewSet(BaseModelViewSet):
    queryset = AttemptAnswer.objects.all()
    serializer_class = AttemptAnswerSerializer
    filterset_class = AttemptAnswerFilter
    search_fields = ["feedback"]
    ordering_fields = "__all__"


class AssignmentViewSet(BaseModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    filterset_class = AssignmentFilter
    search_fields = ["title", "slug", "description"]
    ordering_fields = "__all__"


class AssignmentSubmissionViewSet(BaseModelViewSet):
    queryset = AssignmentSubmission.objects.all()
    serializer_class = AssignmentSubmissionSerializer
    filterset_class = AssignmentSubmissionFilter
    search_fields = ["status", "feedback"]
    ordering_fields = "__all__"
