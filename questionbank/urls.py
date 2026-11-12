
from django.urls import path
from . import views

app_name = "questionbank"

urlpatterns = [
    path(
        "",
        views.question_list,
        name="question_list"
    ),
    path(
        "add/",
        views.question_create,
        name="question_create"
    ),
    path(
        "<int:pk>/edit/",
        views.question_update,
        name="question_update"
    ),
    path(
        "<int:pk>/delete/",
        views.question_delete,
        name="question_delete"
    ),
    path(
        "generate/",
        views.generate_question_set,
        name="generate_question_set"
    ),
]
