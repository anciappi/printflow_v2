from django.contrib import admin
from .models import Supplier, PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('remito_number', 'supplier', 'customer_name', 'status', 'order_date')
    list_filter = ('status', 'supplier')
    inlines = [PurchaseOrderItemInline]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
