from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard')
]