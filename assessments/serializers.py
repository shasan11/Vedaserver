from core.utils.AdaptedBulkSerializer import BulkModelSerializer
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


class QuestionCategorySerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = QuestionCategory
        fields = "__all__"


class QuestionTagSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = QuestionTag
        fields = "__all__"


class QuestionBankSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = QuestionBank
        fields = "__all__"


class QuestionSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Question
        fields = "__all__"


class QuestionOptionSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = QuestionOption
        fields = "__all__"


class QuizSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Quiz
        fields = "__all__"


class QuizQuestionSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = QuizQuestion
        fields = "__all__"


class QuizAttemptSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = QuizAttempt
        fields = "__all__"


class AttemptAnswerSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = AttemptAnswer
        fields = "__all__"


class AssignmentSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Assignment
        fields = "__all__"


class AssignmentSubmissionSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = AssignmentSubmission
        fields = "__all__"
