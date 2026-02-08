from django.urls import path, include
from rest_framework_bulk.routes import BulkRouter

from assessments.views import (
    QuestionCategoryViewSet,
    QuestionTagViewSet,
    QuestionBankViewSet,
    QuestionViewSet,
    QuestionOptionViewSet,
    QuizViewSet,
    QuizQuestionViewSet,
    QuizAttemptViewSet,
    AttemptAnswerViewSet,
    AssignmentViewSet,
    AssignmentSubmissionViewSet,
)

router = BulkRouter()
router.register(r"question-categories", QuestionCategoryViewSet, basename="question-category")
router.register(r"question-tags", QuestionTagViewSet, basename="question-tag")
router.register(r"question-banks", QuestionBankViewSet, basename="question-bank")
router.register(r"questions", QuestionViewSet, basename="question")
router.register(r"question-options", QuestionOptionViewSet, basename="question-option")
router.register(r"quizzes", QuizViewSet, basename="quiz")
router.register(r"quiz-questions", QuizQuestionViewSet, basename="quiz-question")
router.register(r"quiz-attempts", QuizAttemptViewSet, basename="quiz-attempt")
router.register(r"attempt-answers", AttemptAnswerViewSet, basename="attempt-answer")
router.register(r"assignments", AssignmentViewSet, basename="assignment")
router.register(r"assignment-submissions", AssignmentSubmissionViewSet, basename="assignment-submission")

urlpatterns = [
    path("", include(router.urls)),
]
