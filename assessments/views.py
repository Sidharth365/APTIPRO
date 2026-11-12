
import random
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from questionbank.models import Question
from .forms import AssessmentCreateForm
from .models import (
    Assessment,
    AssessmentQuestion,
)


def faculty_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role != "FACULTY":
            return HttpResponseForbidden(
                "Access denied. Only Faculty members can manage assessments."
            )

        return view_func(request, *args, **kwargs)

    return wrapper


@login_required
@faculty_required
def assessment_list(request):

    assessments = Assessment.objects.filter(
        faculty=request.user
    ).prefetch_related("assessment_questions")

    context = {
        "assessments": assessments,
        "total_assessments": assessments.count(),
        "draft_count": assessments.filter(
            status="DRAFT"
        ).count(),
        "scheduled_count": assessments.filter(
            status="SCHEDULED"
        ).count(),
        "live_count": assessments.filter(
            status="LIVE"
        ).count(),
        "completed_count": assessments.filter(
            status="COMPLETED"
        ).count(),
    }

    return render(
        request,
        "assessments/assessment_list.html",
        context
    )


@login_required
@faculty_required
def assessment_create(request):

    if request.method == "POST":

        form = AssessmentCreateForm(
            request.POST,
            user=request.user
        )

        if form.is_valid():

            category = form.cleaned_data["category"]
            difficulty = form.cleaned_data["difficulty"]
            question_count = form.cleaned_data["question_count"]

            available = Question.objects.filter(
                created_by=request.user,
                is_active=True
            )

            if category:
                available = available.filter(category=category)

            if difficulty:
                available = available.filter(
                    difficulty=difficulty
                )

            available_questions = list(available)

            if len(available_questions) < question_count:
                form.add_error(
                    None,
                    "The available question count changed. "
                    "Please check your question bank and try again."
                )

            else:
                selected_questions = random.sample(
                    available_questions,
                    question_count
                )

                if form.cleaned_data["randomize_questions"]:
                    random.shuffle(selected_questions)

                with transaction.atomic():

                    assessment = form.save(commit=False)
                    assessment.faculty = request.user

                    if assessment.scheduled_start:
                        assessment.status = Assessment.Status.SCHEDULED
                    else:
                        assessment.status = Assessment.Status.DRAFT

                    assessment.save()

                    assessment_questions = []

                    for index, question in enumerate(
                        selected_questions,
                        start=1
                    ):
                        assessment_questions.append(
                            AssessmentQuestion(
                                assessment=assessment,
                                question=question,
                                order=index
                            )
                        )

                    AssessmentQuestion.objects.bulk_create(
                        assessment_questions
                    )

                messages.success(
                    request,
                    "Assessment created successfully with "
                    f"{question_count} questions."
                )

                return redirect("assessments:assessment_list")

    else:
        form = AssessmentCreateForm(user=request.user)

    return render(
        request,
        "assessments/assessment_create.html",
        {
            "form": form,
            "page_heading": "Create New Assessment"
        }
    )


@login_required
@faculty_required
def assessment_detail(request, pk):

    assessment = get_object_or_404(
        Assessment.objects.prefetch_related(
            "assessment_questions__question__category"
        ),
        pk=pk,
        faculty=request.user
    )

    return render(
        request,
        "assessments/assessment_detail.html",
        {
            "assessment": assessment,
            "assessment_questions": assessment.assessment_questions.all()
        }
    )
