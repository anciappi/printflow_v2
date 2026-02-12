from django.urls import path
from . import views

urlpatterns = [
    path('', views.indexDashboard, name= 'index' )
]