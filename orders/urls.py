from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.WorkOrderListView.as_view(), name='list'),
    path('nueva/', views.WorkOrderCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.WorkOrderUpdateView.as_view(), name='update'),
]
