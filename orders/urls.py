from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('nueva/', views.create_order, name='order_create'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('<int:pk>/avance/', views.add_production_log, name='add_log'),
    path('<int:pk>/aprobar/', views.approve_order, name='approve_order'),
    path('tablero/', views.OrderListView.as_view(), name='order_list'),
    path('productos/', views.ProductListView.as_view(), name='product_list'),
]