from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.WorkOrderListView.as_view(), name='list'),
    path('new/', views.WorkOrderCreateView.as_view(), name='create'),
    path('load-products/', views.LoadCustomerProductsView.as_view(), name='load_products'),
    path('load-product-details/', views.LoadProductDetailsView.as_view(), name='load_product_details'),
    path('layout-preview/', views.LayoutPreviewView.as_view(), name='layout_preview'),
    path('<int:pk>/', views.WorkOrderDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.WorkOrderUpdateView.as_view(), name='update'),
    path('<int:pk>/status/', views.WorkOrderStatusUpdateView.as_view(), name='status_update'),
    path('<int:pk>/status-modal/', views.WorkOrderStatusUpdateModalView.as_view(), name='status_update_modal'),
    path('<int:pk>/status/revert/', views.WorkOrderStatusRevertView.as_view(), name='status_revert'),
    path('<int:pk>/consumo/', views.WorkOrderConsumoView.as_view(), name='consumo'),
    path('<int:pk>/log/', views.WorkOrderLogCreateView.as_view(), name='add_log'),
    path('log/<int:pk>/edit/', views.WorkOrderLogUpdateView.as_view(), name='edit_log'),
    path('log/<int:pk>/delete/', views.WorkOrderLogDeleteView.as_view(), name='delete_log'),
    path('<int:pk>/partial-log/', views.WorkOrderPartialLogView.as_view(), name='partial_log'),
    path('<int:pk>/stock/', views.WorkOrderStockPanelView.as_view(), name='stock_panel'),
    path('<int:pk>/progress/', views.WorkOrderProgressView.as_view(), name='progress_bar'),
    path('<int:pk>/status-card/', views.WorkOrderProductionStatusCardView.as_view(), name='production_status_card'),
]
