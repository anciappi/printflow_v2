from django.urls import path
from . import views

app_name = 'purchasing'

urlpatterns = [
    # Órdenes de Compra
    path('',                           views.PurchaseOrderListView.as_view(), name='oc_list'),
    path('nueva/',                     views.create_purchase_order,           name='oc_create'),
    path('editar/<int:pk>/',           views.edit_purchase_order,             name='oc_edit'),
    path('eliminar/<int:pk>/',         views.delete_purchase_order,           name='oc_delete'),
    path('recibir/<int:pk>/',          views.recibir_oc,                      name='oc_receive'),

    # Proveedores
    path('proveedores/',               views.SupplierListView.as_view(),      name='supplier_list'),
    path('proveedores/nuevo/',         views.SupplierCreateView.as_view(),    name='supplier_create'),
    path('proveedores/<int:pk>/',      views.SupplierUpdateView.as_view(),    name='supplier_edit'),
]
