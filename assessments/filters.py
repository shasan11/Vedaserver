import django_filters

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


class QuestionCategoryFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    name = django_filters.CharFilter(lookup_expr="icontains")
    slug = django_filters.CharFilter(lookup_expr="iexact")
    parent = django_filters.UUIDFilter(field_name="parent_id")
    active = django_filters.BooleanFilter()

    class Meta:
        model = QuestionCategory
        fields = ["branch", "name", "slug", "parent", "active"]


class QuestionTagFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    name = django_filters.CharFilter(lookup_expr="icontains")
    slug = django_filters.CharFilter(lookup_expr="iexact")
    active = django_filters.BooleanFilter()

    class Meta:
        model = QuestionTag
        fields = ["branch", "name", "slug", "active"]


class QuestionBankFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    name = django_filters.CharFilter(lookup_expr="icontains")
    category = django_filters.UUIDFilter(field_name="category_id")
    active = django_filters.BooleanFilter()

    class Meta:
        model = QuestionBank
        fields = ["branch", "name", "category", "active"]


class QuestionFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    bank = django_filters.UUIDFilter(field_name="bank_id")
    category = django_filters.UUIDFilter(field_name="category_id")
    question_type = django_filters.CharFilter(lookup_expr="iexact")
    difficulty = django_filters.NumberFilter()
    active = django_filters.BooleanFilter()

    class Meta:
        model = Question
        fields = ["branch", "bank", "category", "question_type", "difficulty", "active"]


class QuestionOptionFilter(django_filters.FilterSet):
    question = django_filters.UUIDFilter(field_name="question_id")
    is_correct = django_filters.BooleanFilter()
    active = django_filters.BooleanFilter()

    class Meta:
        model = QuestionOption
        fields = ["question", "is_correct", "active"]


class QuizFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    course = django_filters.UUIDFilter(field_name="course_id")
    status = django_filters.CharFilter(lookup_expr="iexact")
    slug = django_filters.CharFilter(lookup_expr="iexact")
    active = django_filters.BooleanFilter()

    class Meta:
        model = Quiz
        fields = ["branch", "course", "status", "slug", "active"]


class QuizQuestionFilter(django_filters.FilterSet):
    quiz = django_filters.UUIDFilter(field_name="quiz_id")
    question = django_filters.UUIDFilter(field_name="question_id")

    class Meta:
        model = QuizQuestion
        fields = ["quiz", "question"]


class QuizAttemptFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    quiz = django_filters.UUIDFilter(field_name="quiz_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    enrollment = django_filters.UUIDFilter(field_name="enrollment_id")
    status = django_filters.CharFilter(lookup_expr="iexact")
    passed = django_filters.BooleanFilter()

    class Meta:
        model = QuizAttempt
        fields = ["branch", "quiz", "user", "enrollment", "status", "passed"]


class AttemptAnswerFilter(django_filters.FilterSet):
    attempt = django_filters.UUIDFilter(field_name="attempt_id")
    question = django_filters.UUIDFilter(field_name="question_id")
    is_correct = django_filters.BooleanFilter()

    class Meta:
        model = AttemptAnswer
        fields = ["attempt", "question", "is_correct"]


class AssignmentFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    course = django_filters.UUIDFilter(field_name="course_id")
    status = django_filters.CharFilter(lookup_expr="iexact")
    slug = django_filters.CharFilter(lookup_expr="iexact")
    active = django_filters.BooleanFilter()

    class Meta:
        model = Assignment
        fields = ["branch", "course", "status", "slug", "active"]


class AssignmentSubmissionFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    assignment = django_filters.UUIDFilter(field_name="assignment_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    enrollment = django_filters.UUIDFilter(field_name="enrollment_id")
    status = django_filters.CharFilter(lookup_expr="iexact")
    passed = django_filters.BooleanFilter()

    class Meta:
        model = AssignmentSubmission
        fields = ["branch", "assignment", "user", "enrollment", "status", "passed"]
