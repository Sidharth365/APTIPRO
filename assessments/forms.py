
from django import forms
from django.utils import timezone

from questionbank.models import Category, Question
from .models import Assessment


class AssessmentCreateForm(forms.ModelForm):

    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            "class": "form-control"
        })
    )

    difficulty = forms.ChoiceField(
        required=False,
        choices=[
            ("", "All Difficulties"),
            ("EASY", "Easy"),
            ("MEDIUM", "Medium"),
            ("HARD", "Hard"),
        ],
        widget=forms.Select(attrs={
            "class": "form-control"
        })
    )

    question_count = forms.IntegerField(
        min_value=1,
        max_value=100,
        initial=10,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "min": 1,
            "max": 100
        })
    )

    class Meta:
        model = Assessment
        fields = [
            "title",
            "description",
            "total_duration_minutes",
            "scheduled_start",
            "scheduled_end",
            "randomize_questions",
            "randomize_options",
            "allow_question_navigation",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Aptitude Assessment - Test 01"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter assessment instructions..."
            }),

            "total_duration_minutes": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "placeholder": "30"
            }),

            "scheduled_start": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                },
                format="%Y-%m-%dT%H:%M"
            ),

            "scheduled_end": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                },
                format="%Y-%m-%dT%H:%M"
            ),

            "randomize_questions": forms.CheckboxInput(
                attrs={"class": "form-checkbox"}
            ),

            "randomize_options": forms.CheckboxInput(
                attrs={"class": "form-checkbox"}
            ),

            "allow_question_navigation": forms.CheckboxInput(
                attrs={"class": "form-checkbox"}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields["scheduled_start"].required = False
        self.fields["scheduled_end"].required = False

    def clean(self):
        cleaned_data = super().clean()

        start = cleaned_data.get("scheduled_start")
        end = cleaned_data.get("scheduled_end")

        if start and timezone.is_naive(start):
            start = timezone.make_aware(start)

        if end and timezone.is_naive(end):
            end = timezone.make_aware(end)

        if start and start <= timezone.now():
            self.add_error(
                "scheduled_start",
                "Scheduled start must be in the future."
            )

        if start and end and end <= start:
            self.add_error(
                "scheduled_end",
                "End time must be after the start time."
            )

        category = cleaned_data.get("category")
        difficulty = cleaned_data.get("difficulty")
        count = cleaned_data.get("question_count")

        if self.user and count:
            available = Question.objects.filter(
                created_by=self.user,
                is_active=True
            )

            if category:
                available = available.filter(category=category)

            if difficulty:
                available = available.filter(difficulty=difficulty)

            available_count = available.count()

            if available_count < count:
                raise forms.ValidationError(
                    f"Only {available_count} matching active questions "
                    f"are available. You requested {count}. "
                    f"Add more questions or reduce the question count."
                )

        return cleaned_data
