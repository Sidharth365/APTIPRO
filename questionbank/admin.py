
from django.contrib import admin
from .models import Category, Question


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)
    ordering = ("name",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "question_text",
        "category",
        "difficulty",
        "correct_option",
        "time_limit_seconds",
        "marks",
        "is_active",
    )

    list_filter = (
        "category",
        "difficulty",
        "is_active",
    )

    search_fields = (
        "question_text",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
    )

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Question Details", {
            "fields": (
                "category",
                "question_text",
                "difficulty",
            )
        }),
        ("Answer Options", {
            "fields": (
                "option_a",
                "option_b",
                "option_c",
                "option_d",
                "correct_option",
                "explanation",
            )
        }),
        ("Marking and Timing", {
            "fields": (
                "time_limit_seconds",
                "marks",
                "negative_marks",
            )
        }),
        ("Management", {
            "fields": (
                "created_by",
                "is_active",
                "created_at",
                "updated_at",
            )
        }),
    )
