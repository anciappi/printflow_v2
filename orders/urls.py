from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Dashboard Órdenes
    path('', views.OrderListView.as_view(), name='order_list'),
    path('nueva/', views.create_order, name='order_create'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('<int:pk>/avance/', views.add_production_log, name='add_log'),
    path('<int:pk>/aprobar/', views.approve_order, name='approve_order'),

    # Productos
    path('productos/', views.ProductListView.as_view(), name='product_list'),
    path('productos/nuevo/', views.create_product, name='product_create'),
    path('producto/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
]