from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Sum, Q
from django.shortcuts import render
from django.http import HttpResponseRedirect
from decimal import Decimal
from .models import *
from purchasing.models import PurchaseOrder, PurchaseOrderItem, Supplier

# --- 1. Formularios y Configuración de Inlines ---
class ConsumptionInline(admin.TabularInline):
    model = ConsumptionLog
    extra = 1
    fields = ('quantity_used', 'responsible', 'date')
    readonly_fields = ('date',)

# --- 2. Gestión Gerencial (El Dashboard que Gerencia Ama) ---
@admin.register(MaterialStockSummary)
class MaterialStockSummaryAdmin(admin.ModelAdmin):
    # Añadimos 'technology' a la vista principal
    list_display = (
        'name', 
        'material_type', 
        'get_specs', 
        'technology',  # <-- Crucial para los Chips
        'total_units', 
        'total_stock_qty'
    )
    list_filter = ('material_type', 'technology', 'brand')
    search_fields = ('name', 'technology', 'brand')

    def get_specs(self, obj):
        # Muestra el "DNI" físico del material
        return f"{obj.width or '0'}x{obj.length or '0'} | {obj.grammage or '0'}g"
    get_specs.short_description = "Especificaciones (Ancho x Largo | Gr)"

    def total_units(self, obj):
        # Cuenta cuántas bobinas/rollos físicos hay en el rack (que no estén agotados)
        count = obj.units.filter(~Q(status='EXHAUSTED')).count()
        return f"{count} unidades"
    total_units.short_description = "Unid. en Rack"

    def total_stock_qty(self, obj):
        # Suma total de metros o unidades disponibles
        total = obj.units.filter(~Q(status='EXHAUSTED')).aggregate(Sum('current_quantity'))['current_quantity__sum'] or 0
        return f"{total} totales"
    total_stock_qty.short_description = "Cantidad Total"

# --- 3. Gestión de Depósito (Unidades Individuales) ---
@admin.register(InventoryUnit)
class InventoryUnitAdmin(admin.ModelAdmin):
    list_display = (
        'get_remito', 
        'unit_number', 
        'material', 
        'get_entry_date', 
        'get_current_width', 
        'current_quantity', 
        'status', 
        'get_customer'
    )
    list_filter = ('status', 'material', 'branch')
    ordering = ('purchase_order', 'unit_number')
    inlines = [ConsumptionInline]
    actions = ['fraccionar_bobina_action']

    # Funciones de columnas
    def get_remito(self, obj): return obj.purchase_order.remito_number
    get_remito.short_description = "Remito"

    def get_entry_date(self, obj): return obj.purchase_order.delivery_date
    get_entry_date.short_description = "Fecha Ingreso"

    def get_customer(self, obj): return obj.purchase_order.customer_name
    get_customer.short_description = "Cliente"

    def get_current_width(self, obj): return f"{obj.get_width()} cm"
    get_current_width.short_description = "Ancho Real"

    @admin.action(description="✂️ Fraccionar Bobina (Corte A + B)")
    def fraccionar_bobina_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Seleccioná solo una bobina.", messages.WARNING)
            return
        
        obj = queryset.first()
        ancho_total = obj.get_width()

        if 'post' in request.POST:
            ancho_a = Decimal(request.POST.get('ancho_a'))
            ancho_b = ancho_total - ancho_a
            
            with transaction.atomic():
                InventoryUnit.objects.create(
                    material=obj.material, purchase_order=obj.purchase_order,
                    unit_number=f"{obj.unit_number}.a", branch=obj.branch,
                    initial_quantity=obj.current_quantity, current_quantity=obj.current_quantity,
                    width_override=ancho_a, parent_unit=obj
                )
                InventoryUnit.objects.create(
                    material=obj.material, purchase_order=obj.purchase_order,
                    unit_number=f"{obj.unit_number}.b", branch=obj.branch,
                    initial_quantity=obj.current_quantity, current_quantity=obj.current_quantity,
                    width_override=ancho_b, parent_unit=obj
                )
                obj.status = 'EXHAUSTED'; obj.current_quantity = 0; obj.save()
            
            self.message_user(request, "Fraccionamiento exitoso.")
            return HttpResponseRedirect(request.get_full_path())

        return render(request, 'admin/inventory/fraccionar_form.html', {
            'unit': obj, 'ancho_total': ancho_total, 'opts': self.model._meta,
        })

# --- 4. (Purchasing now handled in purchasing/admin.py) ---

# --- 5. Definición de Materiales con Especificaciones ---
@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'material_type', 'brand', 'get_specs', 'technology')
    list_filter = ('material_type', 'brand', 'technology')
    
    fieldsets = (
        ('Información Básica', {'fields': ('name', 'material_type', 'brand', 'standard_quantity')}),
        ('Especificaciones Físicas', {'fields': ('grammage', 'width', 'length')}),
        ('Atributos Chips/Bandas', {'classes': ('collapse',), 'fields': ('mag_stripe_width', 'technology', 'position')}),
    )

    def get_specs(self, obj):
        return f"{obj.width or '0'}x{obj.length or '0'} | {obj.grammage or '0'}g"
    get_specs.short_description = "Especificaciones"

# --- 6. Registros Básicos ---
admin.site.register(Branch)
# Note: Supplier is now registered in purchasing/admin.py