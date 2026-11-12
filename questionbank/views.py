
from functools import wraps
import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import render, redirect, get_object_or_404

from .models import Question, Category
from .forms import QuestionForm


# ==========================================
# FACULTY ACCESS DECORATOR
# ==========================================

def faculty_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role != "FACULTY":
            messages.error(
                request,
                "You are not authorized to access the Faculty Question Bank."
            )
            return redirect("dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper


# ==========================================
# QUESTION LIST
# ==========================================

@login_required
@faculty_required
def question_list(request):

    questions = Question.objects.filter(
        created_by=request.user
    ).select_related("category").order_by("-created_at")

    search_query = request.GET.get("search", "").strip()
    category_id = request.GET.get("category", "")
    difficulty = request.GET.get("difficulty", "")
    status = request.GET.get("status", "")

    # Search questions
    if search_query:
        questions = questions.filter(
            Q(question_text__icontains=search_query)
            | Q(option_a__icontains=search_query)
            | Q(option_b__icontains=search_query)
            | Q(option_c__icontains=search_query)
            | Q(option_d__icontains=search_query)
        )

    # Filter by category
    if category_id:
        questions = questions.filter(category_id=category_id)

    # Filter by difficulty
    if difficulty:
        questions = questions.filter(difficulty=difficulty)

    # Filter by active/inactive status
    if status == "active":
        questions = questions.filter(is_active=True)
    elif status == "inactive":
        questions = questions.filter(is_active=False)

    paginator = Paginator(questions, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "questions": page_obj,
        "page_obj": page_obj,
        "categories": Category.objects.filter(is_active=True),
        "search_query": search_query,
        "selected_category": category_id,
        "selected_difficulty": difficulty,
        "selected_status": status,
        "total_questions": questions.count(),
    }

    return render(
        request,
        "questionbank/question_list.html",
        context
    )


# ==========================================
# ADD QUESTION
# ==========================================

@login_required
@faculty_required
def question_create(request):

    if request.method == "POST":

        form = QuestionForm(request.POST)

        if form.is_valid():

            question = form.save(commit=False)
            question.created_by = request.user
            question.save()

            messages.success(
                request,
                "Question added successfully!"
            )

            return redirect("questionbank:question_list")

        messages.error(
            request,
            "Please correct the errors in the form."
        )

    else:
        form = QuestionForm()

    return render(
        request,
        "questionbank/question_form.html",
        {
            "form": form,
            "page_title": "Add New Question",
            "button_text": "Save Question",
        }
    )


# ==========================================
# EDIT QUESTION
# ==========================================

@login_required
@faculty_required
def question_update(request, pk):

    question = get_object_or_404(
        Question,
        pk=pk,
        created_by=request.user
    )

    if request.method == "POST":

        form = QuestionForm(
            request.POST,
            instance=question
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Question updated successfully!"
            )

            return redirect("questionbank:question_list")

        messages.error(
            request,
            "Please correct the errors in the form."
        )

    else:
        form = QuestionForm(instance=question)

    return render(
        request,
        "questionbank/question_form.html",
        {
            "form": form,
            "question": question,
            "page_title": "Edit Question",
            "button_text": "Update Question",
        }
    )


# ==========================================
# DELETE QUESTION
# ==========================================

@login_required
@faculty_required
def question_delete(request, pk):

    question = get_object_or_404(
        Question,
        pk=pk,
        created_by=request.user
    )

    if request.method == "POST":

        try:
            question.delete()

            messages.success(
                request,
                "Question deleted successfully!"
            )

        except ProtectedError:

            messages.warning(
                request,
                "This question is already used in an assessment. "
                "Deactivate it instead of deleting it."
            )

        return redirect("questionbank:question_list")

    return render(
        request,
        "questionbank/question_confirm_delete.html",
        {
            "question": question
        }
    )


# ==========================================
# AUTO GENERATE QUESTION SET
# ==========================================

@login_required
@faculty_required
def generate_question_set(request):

    categories = Category.objects.filter(
        is_active=True
    ).order_by("name")

    generated_questions = []

    if request.method == "POST":

        category_id = request.POST.get("category")
        difficulty = request.POST.get("difficulty")
        count_value = request.POST.get("count", "10")

        # Validate category
        category = get_object_or_404(
            Category,
            id=category_id,
            is_active=True
        )

        # Validate difficulty
        valid_difficulties = ["EASY", "MEDIUM", "HARD"]

        if difficulty not in valid_difficulties:

            messages.error(
                request,
                "Please select a valid difficulty level."
            )

        else:

            # Validate number of questions
            try:
                question_count = int(count_value)

                if question_count < 1 or question_count > 100:
                    raise ValueError

            except (ValueError, TypeError):

                question_count = 0

                messages.error(
                    request,
                    "Enter a number of questions between 1 and 100."
                )

            if question_count:

                # Get faculty's own active questions
                available_questions = list(
                    Question.objects.filter(
                        created_by=request.user,
                        category=category,
                        difficulty=difficulty,
                        is_active=True
                    ).select_related("category")
                )

                available_count = len(available_questions)

                # Check if enough questions exist
                if available_count < question_count:

                    messages.error(
                        request,
                        f"Only {available_count} active "
                        f"{difficulty.lower()} questions are available "
                        f"in {category.name}. "
                        f"You requested {question_count}."
                    )

                else:

                    # Randomly select questions
                    generated_questions = random.sample(
                        available_questions,
                        question_count
                    )

                    messages.success(
                        request,
                        f"{question_count} questions generated successfully!"
                    )

    context = {
        "categories": categories,
        "generated_questions": generated_questions,
    }

    return render(
        request,
        "questionbank/generate_set.html",
        context
    )
