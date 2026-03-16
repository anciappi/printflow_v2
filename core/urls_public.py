"""
Public schema URL configuration for PrintFlow.
This file handles URLs for the public schema only (superadmin, landing).
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='public/landing.html'), name='landing'),
]
