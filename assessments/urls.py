
from django.urls import path
from . import views

app_name = "assessments"

urlpatterns = [
    path(
        "",
        views.assessment_list,
        name="assessment_list"
    ),

    path(
        "create/",
        views.assessment_create,
        name="assessment_create"
    ),

    path(
        "<int:pk>/",
        views.assessment_detail,
        name="assessment_detail"
    ),
]
