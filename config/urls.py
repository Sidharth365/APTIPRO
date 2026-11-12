
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # Question Bank
    path(
        "faculty/question-bank/",
        include(
            ("questionbank.urls", "questionbank"),
            namespace="questionbank"
        )
    ),

    # Assessments
    path(
        "faculty/assessments/",
        include(
            ("assessments.urls", "assessments"),
            namespace="assessments"
        )
    ),

    # Accounts, Login, Registration and Dashboards
    path("", include("accounts.urls")),
]
