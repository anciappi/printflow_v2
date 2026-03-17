"""
Public schema URL configuration for PrintFlow.
Handles URLs for the public schema only (superadmin, landing).
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', TemplateView.as_view(
        template_name='public/landing.html'
    ), name='landing'),
]
