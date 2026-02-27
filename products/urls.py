from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('catalogo/', views.product_catalog, name='catalog'),
    path('nuevo/', views.product_create, name='create'),
]