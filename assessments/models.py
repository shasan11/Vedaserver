# assessments/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

from core.utils.coreModels import StampedOwnedActive, BranchScopedStampedOwnedActive


# ----------------------------- choices -----------------------------

class QuizStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class QuestionType(models.TextChoices):
    SINGLE_CHOICE = "single_choice", "Single Choice (MCQ)"
    MULTI_CHOICE = "multi_choice", "Multiple Choice"
    TRUE_FALSE = "true_false", "True/False"
    SHORT_TEXT = "short_text", "Short Answer"
    LONG_TEXT = "long_text", "Long Answer"
    NUMERIC = "numeric", "Numeric"


class AttemptStatus(models.TextChoices):
    STARTED = "started", "Started"
    SUBMITTED = "submitted", "Submitted"
    GRADED = "graded", "Graded"
    EXPIRED = "expired", "Expired"
    CANCELLED = "cancelled", "Cancelled"


class AssignmentStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class SubmissionStatus(models.TextChoices):
    SUBMITTED = "submitted", "Submitted"
    GRADED = "graded", "Graded"
    RETURNED = "returned", "Returned"
    RESUBMITTED = "resubmitted", "Resubmitted"


class SubmissionType(models.TextChoices):
    TEXT = "text", "Text"
    FILE = "file", "File"
    BOTH = "both", "Text + File"
    LINK = "link", "Link"


# ----------------------------- question bank -----------------------------

class QuestionCategory(BranchScopedStampedOwnedActive):
    name = models.CharField(max_length=120, db_index=True)
    slug = models.SlugField(max_length=140, db_index=True)

    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="children",
    )

    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "question_categories"
        ordering = ["sort_order", "name"]
        constraints = [
            models.UniqueConstraint(fields=["branch", "slug"], name="uniq_question_category_branch_slug")
        ]

    def __str__(self):
        return self.name


class QuestionTag(BranchScopedStampedOwnedActive):
    name = models.CharField(max_length=80, db_index=True)
    slug = models.SlugField(max_length=100, db_index=True)

    class Meta:
        db_table = "question_tags"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["branch", "slug"], name="uniq_question_tag_branch_slug")
        ]

    def __str__(self):
        return self.name


class QuestionBank(BranchScopedStampedOwnedActive):
    """
    Container for reusable questions (by subject, topic, or exam type).
    """

    name = models.CharField(max_length=160, db_index=True)
    description = models.TextField(blank=True, null=True)

    category = models.ForeignKey(
        QuestionCategory,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="banks",
    )

    tags = models.ManyToManyField(QuestionTag, blank=True, related_name="banks")

    class Meta:
        db_table = "question_banks"
        indexes = [
            models.Index(fields=["branch", "active"]),
        ]

    def __str__(self):
        return self.name


class Question(BranchScopedStampedOwnedActive):
    """
    The actual question.
    For choice questions, answers live in QuestionOption.
    For text/numeric, answer key fields live here (optional if you want manual grading).
    """

    bank = models.ForeignKey(
        QuestionBank,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="questions",
        db_index=True,
    )

    category = models.ForeignKey(
        QuestionCategory,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="questions",
    )

    tags = models.ManyToManyField(QuestionTag, blank=True, related_name="questions")

    question_type = models.CharField(max_length=30, choices=QuestionType.choices, db_index=True)

    title = models.CharField(max_length=255, blank=True, null=True)  # optional short heading
    prompt = models.TextField()  # store HTML/MD if you want
    explanation = models.TextField(blank=True, null=True)  # solution/explanation for review

    difficulty = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1=Easy ... 5=Hard",
        db_index=True,
    )

    default_marks = models.DecimalField(max_digits=10, decimal_places=2, default=1, validators=[MinValueValidator(0)])

    # ---- answer keys for non-choice questions (optional) ----
    # SHORT_TEXT: list of accepted answers (case sensitivity configurable)
    correct_text_answers = models.JSONField(default=list, blank=True)
    case_sensitive = models.BooleanField(default=False)

    # NUMERIC: correct number with tolerance
    correct_number = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    tolerance = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True, default=Decimal("0"))

    # LONG_TEXT usually manual graded → leave answer keys empty

    class Meta:
        db_table = "questions"
        indexes = [
            models.Index(fields=["branch", "question_type"]),
            models.Index(fields=["difficulty"]),
            models.Index(fields=["bank"]),
        ]

    def __str__(self):
        return f"{self.question_type}: {self.title or self.prompt[:60]}"

    @property
    def is_choice(self):
        return self.question_type in (QuestionType.SINGLE_CHOICE, QuestionType.MULTI_CHOICE, QuestionType.TRUE_FALSE)

    @property
    def is_auto_gradable(self):
        # long text is usually manual
        if self.question_type == QuestionType.LONG_TEXT:
            return False
        # text/numeric can be auto-graded only if keys are present
        if self.question_type == QuestionType.SHORT_TEXT:
            return bool(self.correct_text_answers)
        if self.question_type == QuestionType.NUMERIC:
            return self.correct_number is not None
        return True


class QuestionOption(StampedOwnedActive):
    """
    Options for MCQ / multi-choice / true-false.
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options", db_index=True)

    text = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)

    is_correct = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "question_options"
        ordering = ["sort_order", "id"]
        indexes = [
            models.Index(fields=["question", "sort_order"]),
        ]

    def __str__(self):
        return f"Option({self.question_id})"


# ----------------------------- quiz -----------------------------

class Quiz(BranchScopedStampedOwnedActive):
    """
    A quiz belongs to a course. Can be linked from a Lesson (content app already references Quiz).
    """

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="quizzes",
        db_index=True,
    )

    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, db_index=True)

    description = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=QuizStatus.choices, default=QuizStatus.DRAFT, db_index=True)

    total_marks = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    pass_marks = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    time_limit_minutes = models.PositiveIntegerField(blank=True, null=True)  # None = unlimited
    attempts_allowed = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])

    shuffle_questions = models.BooleanField(default=False)
    shuffle_options = models.BooleanField(default=False)

    show_result_after_submit = models.BooleanField(default=True)
    show_correct_answers = models.BooleanField(default=False)  # typically after quiz end

    available_from = models.DateTimeField(blank=True, null=True, db_index=True)
    available_until = models.DateTimeField(blank=True, null=True, db_index=True)

    published_at = models.DateTimeField(blank=True, null=True, db_index=True)

    # extra behavior knobs without migrations every week
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "quizzes"
        constraints = [
            models.UniqueConstraint(fields=["course", "slug"], name="uniq_course_quiz_slug"),
        ]
        indexes = [
            models.Index(fields=["course", "status"]),
            models.Index(fields=["branch", "status"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.course_id and self.branch_id is None:
            self.branch = self.course.branch
        super().save(*args, **kwargs)

    def publish(self):
        self.status = QuizStatus.PUBLISHED
        if not self.published_at:
            self.published_at = timezone.now()
        self.save(update_fields=["status", "published_at"])


class QuizQuestion(StampedOwnedActive):
    """
    Assign questions to quiz with order and marks override.
    """

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="quiz_questions", db_index=True)
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="used_in_quizzes", db_index=True)

    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    marks = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])

    class Meta:
        db_table = "quiz_questions"
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["quiz", "question"], name="uniq_quiz_question"),
        ]
        indexes = [
            models.Index(fields=["quiz", "sort_order"]),
        ]

    def __str__(self):
        return f"{self.quiz_id} -> {self.question_id}"


# ----------------------------- attempts + answers -----------------------------

class QuizAttempt(BranchScopedStampedOwnedActive):
    """
    One attempt by a user.
    """

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts", db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_attempts", db_index=True)

    enrollment = models.ForeignKey(
        "enrollments.Enrollment",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="quiz_attempts",
        db_index=True,
    )

    status = models.CharField(max_length=20, choices=AttemptStatus.choices, default=AttemptStatus.STARTED, db_index=True)

    started_at = models.DateTimeField(default=timezone.now, db_index=True)
    submitted_at = models.DateTimeField(blank=True, null=True, db_index=True)
    graded_at = models.DateTimeField(blank=True, null=True, db_index=True)

    time_taken_seconds = models.PositiveIntegerField(default=0)

    total_marks = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    marks_obtained = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    percent = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], db_index=True)

    passed = models.BooleanField(default=False, db_index=True)

    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "quiz_attempts"
        indexes = [
            models.Index(fields=["quiz", "status"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["submitted_at"]),
        ]

    def __str__(self):
        return f"Attempt({self.user_id}::{self.quiz_id}::{self.status})"

    def save(self, *args, **kwargs):
        if self.quiz_id and self.branch_id is None:
            self.branch = self.quiz.branch
        super().save(*args, **kwargs)


class AttemptAnswer(StampedOwnedActive):
    """
    Answer for one question within an attempt.
    For choice questions: selected_options M2M.
    For text: text_answer.
    For numeric: number_answer.
    """

    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="answers", db_index=True)
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="attempt_answers", db_index=True)

    # Choice selections
    selected_options = models.ManyToManyField(QuestionOption, blank=True, related_name="selected_in_answers")

    # Text/numeric
    text_answer = models.TextField(blank=True, null=True)
    number_answer = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)

    # grading
    is_correct = models.BooleanField(default=False, db_index=True)
    marks_awarded = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    feedback = models.TextField(blank=True, null=True)

    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="answers_graded",
    )
    graded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "attempt_answers"
        constraints = [
            models.UniqueConstraint(fields=["attempt", "question"], name="uniq_attempt_question_answer"),
        ]
        indexes = [
            models.Index(fields=["attempt"]),
            models.Index(fields=["question"]),
            models.Index(fields=["is_correct"]),
        ]

    def __str__(self):
        return f"Ans({self.attempt_id}::{self.question_id})"


# ----------------------------- assignments -----------------------------

class Assignment(BranchScopedStampedOwnedActive):
    """
    Assignment for a course. Can be linked from Lesson via content app FK.
    """

    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="assignments", db_index=True)

    title = models.CharField(max_length=220, db_index=True)
    slug = models.SlugField(max_length=240, db_index=True)

    description = models.TextField(blank=True, null=True)  # instructions
    status = models.CharField(max_length=20, choices=AssignmentStatus.choices, default=AssignmentStatus.DRAFT, db_index=True)

    submission_type = models.CharField(max_length=10, choices=SubmissionType.choices, default=SubmissionType.FILE)

    max_marks = models.DecimalField(max_digits=10, decimal_places=2, default=100, validators=[MinValueValidator(0)])
    pass_marks = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    allow_resubmission = models.BooleanField(default=True)
    due_at = models.DateTimeField(blank=True, null=True, db_index=True)

    published_at = models.DateTimeField(blank=True, null=True, db_index=True)

    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "assignments"
        constraints = [
            models.UniqueConstraint(fields=["course", "slug"], name="uniq_course_assignment_slug"),
        ]
        indexes = [
            models.Index(fields=["course", "status"]),
            models.Index(fields=["branch", "status"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.course_id and self.branch_id is None:
            self.branch = self.course.branch
        super().save(*args, **kwargs)


class AssignmentSubmission(BranchScopedStampedOwnedActive):
    """
    Student submission.
    """

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions", db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assignment_submissions", db_index=True)

    enrollment = models.ForeignKey(
        "enrollments.Enrollment",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="assignment_submissions",
        db_index=True,
    )

    status = models.CharField(max_length=20, choices=SubmissionStatus.choices, default=SubmissionStatus.SUBMITTED, db_index=True)

    submitted_at = models.DateTimeField(default=timezone.now, db_index=True)

    # payloads
    text_answer = models.TextField(blank=True, null=True)
    link_url = models.URLField(blank=True, null=True)

    file_url = models.URLField(blank=True, null=True)
    storage_key = models.CharField(max_length=255, blank=True, null=True)
    original_name = models.CharField(max_length=255, blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    size_bytes = models.BigIntegerField(blank=True, null=True)

    # grading
    marks_awarded = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    passed = models.BooleanField(default=False, db_index=True)
    feedback = models.TextField(blank=True, null=True)

    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="assignment_submissions_graded",
    )
    graded_at = models.DateTimeField(blank=True, null=True)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "assignment_submissions"
        indexes = [
            models.Index(fields=["assignment", "status"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["submitted_at"]),
        ]
        constraints = [
            # One active submission per assignment per user.
            models.UniqueConstraint(fields=["assignment", "user"], name="uniq_assignment_user_submission")
        ]

    def __str__(self):
        return f"Submission({self.user_id}::{self.assignment_id})"

    def save(self, *args, **kwargs):
        if self.assignment_id and self.branch_id is None:
            self.branch = self.assignment.branch
        super().save(*args, **kwargs)
