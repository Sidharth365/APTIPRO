
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Assessment(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SCHEDULED = "SCHEDULED", "Scheduled"
        LIVE = "LIVE", "Live"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="faculty_assessments"
    )

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.DRAFT
    )

    total_duration_minutes = models.PositiveIntegerField(
        default=20,
        validators=[MinValueValidator(1)]
    )

    scheduled_start = models.DateTimeField(
        null=True,
        blank=True
    )

    scheduled_end = models.DateTimeField(
        null=True,
        blank=True
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    randomize_questions = models.BooleanField(default=False)

    randomize_options = models.BooleanField(default=False)

    allow_question_navigation = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["scheduled_start"]),
            models.Index(fields=["faculty", "status"]),
        ]

    def clean(self):
        super().clean()

        if (
            self.scheduled_start
            and self.scheduled_end
            and self.scheduled_end <= self.scheduled_start
        ):
            raise ValidationError({
                "scheduled_end": "End time must be after start time."
            })

    def __str__(self):
        return self.title

    @property
    def total_questions(self):
        return self.assessment_questions.count()


class AssessmentQuestion(models.Model):
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="assessment_questions"
    )

    question = models.ForeignKey(
        "questionbank.Question",
        on_delete=models.PROTECT,
        related_name="assessment_uses"
    )

    order = models.PositiveIntegerField(default=1)

    # Snapshot values preserve the assessment settings
    # even if the original question is edited later.
    marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )

    negative_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )

    time_limit_seconds = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["assessment", "question"],
                name="unique_question_per_assessment"
            ),
            models.UniqueConstraint(
                fields=["assessment", "order"],
                name="unique_question_order_per_assessment"
            ),
        ]

    def __str__(self):
        return f"{self.assessment.title} - Question {self.order}"

    @property
    def effective_marks(self):
        return self.marks if self.marks is not None else self.question.marks

    @property
    def effective_negative_marks(self):
        return (
            self.negative_marks
            if self.negative_marks is not None
            else self.question.negative_marks
        )

    @property
    def effective_time_limit(self):
        return (
            self.time_limit_seconds
            if self.time_limit_seconds is not None
            else self.question.time_limit_seconds
        )


class AssessmentNotification(models.Model):
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assessment_notifications"
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["assessment", "student"],
                name="unique_assessment_student_notification"
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.assessment.title}"
