from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('dashboard/', views.StockDashboardView.as_view(), name='dashboard'),
    path('unidades/', views.InventoryListView.as_view(), name='inventory_list'),
    
    # Rutas de Consumo y Recepción
    path('consumo/<int:unit_id>/', views.registrar_consumo, name='registrar_consumo'), # <--- Verificar esta
    path('remitos/', views.OCListView.as_view(), name='oc_list'),
    path('remitos/recibir/<int:pk>/', views.recibir_oc, name='oc_receive'),
    path('remitos/nuevo/', views.create_purchase_order, name='oc_create'),

    # --- RUTAS NUEVAS (Verifica que estén aquí) ---
    path('proveedores/nuevo/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('materiales/nuevo/', views.MaterialCreateView.as_view(), name='material_create'),
    path('remitos/editar/<int:pk>/', views.edit_purchase_order, name='oc_edit'),
    path('remitos/eliminar/<int:pk>/', views.delete_purchase_order, name='oc_delete'),
    path('fraccionar/<int:unit_id>/', views.fraccionar_unidad, name='fraccionar_unidad'),
    path('historial-consumo/', views.ConsumptionHistoryView.as_view(), name='consumption_history'),
    path('consumo/eliminar/<int:log_id>/', views.eliminar_consumo, name='eliminar_consumo'),
    path('fraccionar/deshacer/<int:unit_id>/', views.deshacer_fraccionamiento, name='deshacer_fraccionamiento'),

    #Listado de materiales
    path('materiales/', views.MaterialListView.as_view(), name='material_list'),
    path('materiales/editar/<int:pk>/', views.MaterialUpdateView.as_view(), name='material_edit'),
    path('materiales/borrar/<int:pk>/', views.MaterialDeleteView.as_view(), name='material_delete'),
]