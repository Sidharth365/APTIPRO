
from django.contrib import admin
from .models import (
    Assessment,
    AssessmentQuestion,
    AssessmentNotification,
)


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "faculty",
        "status",
        "total_duration_minutes",
        "scheduled_start",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = ("title", "faculty__username")
    readonly_fields = (
        "faculty",
        "status",
        "started_at",
        "completed_at",
        "created_at",
        "updated_at",
    )

    # Platform administrators can monitor assessments,
    # but cannot create, edit, or delete them.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "assessment",
        "question",
        "order",
        "marks",
        "negative_marks",
        "time_limit_seconds",
    )

    list_filter = ("assessment__status",)
    search_fields = ("assessment__title", "question__question_text")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AssessmentNotification)
class AssessmentNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "assessment",
        "student",
        "is_read",
        "created_at",
    )

    list_filter = ("is_read", "created_at")
    search_fields = (
        "assessment__title",
        "student__username",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
