
from django import forms
from .models import Category, Question


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question

        fields = [
            "category",
            "question_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_option",
            "explanation",
            "difficulty",
            "time_limit_seconds",
            "marks",
            "negative_marks",
            "is_active",
        ]

        widgets = {
            "category": forms.Select(attrs={"class": "form-control"}),
            "question_text": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Enter your question..."
            }),
            "option_a": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter option A"
            }),
            "option_b": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter option B"
            }),
            "option_c": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter option C"
            }),
            "option_d": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter option D"
            }),
            "correct_option": forms.Select(attrs={
                "class": "form-control"
            }),
            "explanation": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
            "difficulty": forms.Select(attrs={
                "class": "form-control"
            }),
            "time_limit_seconds": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1
            }),
            "marks": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "step": "0.25"
            }),
            "negative_marks": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "step": "0.25"
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-checkbox"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = Category.objects.filter(
            is_active=True
        )

        self.fields["explanation"].required = False
