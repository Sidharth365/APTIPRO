
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone

from .forms import RegisterForm

User = get_user_model()


# --------------------------------
# HOME PAGE
# --------------------------------

def home(request):
    return render(request, "home.html")


# --------------------------------
# USER REGISTRATION
# --------------------------------

def register(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            messages.success(
                request,
                "Your AptiPro account has been created successfully. Please log in."
            )

            return redirect("login")

        else:
            messages.error(
                request,
                "Please correct the errors in the registration form."
            )

    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form}
    )


# --------------------------------
# LOGIN
# --------------------------------

class AptiProLoginView(LoginView):

    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):

        user = self.request.user

        if user.is_superuser:
            return "/admin-dashboard/"

        return "/dashboard/"

    def form_valid(self, form):

        messages.success(
            self.request,
            f"Welcome back, {form.get_user().get_username()}!"
        )

        return super().form_valid(form)


# --------------------------------
# LOGOUT
# --------------------------------

class AptiProLogoutView(LogoutView):

    next_page = "home"

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            messages.info(request, "You have been logged out.")

        return super().dispatch(request, *args, **kwargs)


# --------------------------------
# USER DASHBOARD
# --------------------------------


@login_required
def dashboard(request):

    # Super Admin
    if request.user.is_superuser:
        return redirect("admin_dashboard")

    # Faculty
    if request.user.role == "FACULTY":
        return redirect("faculty_dashboard")

    # College Admin
    if request.user.role == "COLLEGE_ADMIN":
        return redirect("admin_dashboard")

    # Student
    return render(request, "dashboard/dashboard.html")


# --------------------------------
# ADMIN PERMISSION CHECK
# --------------------------------

def is_apti_admin(user):

    return user.is_authenticated and user.is_superuser


# --------------------------------
# ADMIN DASHBOARD
# --------------------------------

@login_required
@user_passes_test(is_apti_admin)
def admin_dashboard(request):

    total_users = User.objects.count()

    # Role-based counts
    students = User.objects.filter(role="STUDENT").count()
    faculty = User.objects.filter(role="FACULTY").count()
    college_admins = User.objects.filter(role="COLLEGE_ADMIN").count()

    # Recently registered users
    recent_users = User.objects.order_by("-date_joined")[:8]

    # User registration statistics
    user_roles = (
        User.objects.values("role")
        .annotate(total=Count("id"))
        .order_by("role")
    )

    # New users registered today
    today = timezone.localdate()

    new_users_today = User.objects.filter(
        date_joined__date=today
    ).count()

    context = {
        "total_users": total_users,
        "students": students,
        "faculty": faculty,
        "college_admins": college_admins,
        "new_users_today": new_users_today,
        "recent_users": recent_users,
        "user_roles": user_roles,
    }

    return render(
        request,
        "dashboard/admin_dashboard.html",
        context
    )


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from questionbank.models import Question
from assessments.models import Assessment


@login_required
def faculty_dashboard(request):

    if request.user.role != "FACULTY":
        return redirect("dashboard")

    faculty_assessments = Assessment.objects.filter(
        faculty=request.user
    )

    context = {
        "total_questions": Question.objects.filter(
            created_by=request.user
        ).count(),

        "active_questions": Question.objects.filter(
            created_by=request.user,
            is_active=True
        ).count(),

        "total_assessments": faculty_assessments.count(),

        "draft_count": faculty_assessments.filter(
            status="DRAFT"
        ).count(),

        "scheduled_count": faculty_assessments.filter(
            status="SCHEDULED"
        ).count(),

        "live_count": faculty_assessments.filter(
            status="LIVE"
        ).count(),

        "completed_count": faculty_assessments.filter(
            status="COMPLETED"
        ).count(),

        "recent_assessments": faculty_assessments.order_by(
            "-created_at"
        )[:5],
    }

    return render(
        request,
        "dashboard/faculty_dashboard.html",
        context
    )
