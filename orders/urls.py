from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.WorkOrderListView.as_view(), name='list'),
    path('new/', views.WorkOrderCreateView.as_view(), name='create'),
    path('load-products/', views.LoadCustomerProductsView.as_view(), name='load_products'),
    path('<int:pk>/', views.WorkOrderDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.WorkOrderUpdateView.as_view(), name='update'),
    path('<int:pk>/status/', views.WorkOrderStatusUpdateView.as_view(), name='status_update'),
    path('<int:pk>/consumo/', views.WorkOrderConsumoView.as_view(), name='consumo'),
    path('<int:pk>/stock/', views.WorkOrderStockPanelView.as_view(), name='stock_panel'),
    path('<int:pk>/progress/', views.WorkOrderProgressView.as_view(), name='progress_bar'),
]
