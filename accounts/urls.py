
from django.urls import path

from . import views
from .views import (
    AptiProLoginView,
    AptiProLogoutView,
)

urlpatterns = [
    # Home
    path("", views.home, name="home"),

    # Student Registration
    path("register/", views.register, name="register"),

    # Login and Logout
    path("login/", AptiProLoginView.as_view(), name="login"),
    path("logout/", AptiProLogoutView.as_view(), name="logout"),

    # General Dashboard (redirects based on user role)
    path("dashboard/", views.dashboard, name="dashboard"),

    # Faculty Dashboard
    path(
        "faculty-dashboard/",
        views.faculty_dashboard,
        name="faculty_dashboard"
    ),

    # Admin Dashboard
    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),
]
