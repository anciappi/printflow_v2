from django.contrib import admin, messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Order, OrderItem, CardSpecification, TicketSpecification, ProductionLog

# --- 1. CONFIGURACIÓN DE LOS INLINES ---
# Esto permite editar todo desde la misma página de la OT

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class CardSpecificationInline(admin.StackedInline):
    model = CardSpecification
    can_delete = False
    verbose_name = "Especificaciones Magtick (Tarjetas)"

class TicketSpecificationInline(admin.StackedInline):
    model = TicketSpecification
    can_delete = False
    verbose_name = "Especificaciones Velton (Tickets)"

class ProductionLogInline(admin.TabularInline):
    model = ProductionLog
    extra = 1
    readonly_fields = ('created_at',)
    # Evitamos que el operario tenga que seleccionar su nombre, lo haremos automático
    fields = ('stage', 'operator', 'good_units', 'bad_units', 'created_at')

# --- 2. CONFIGURACIÓN DEL MODELO PRINCIPAL (ORDER) ---

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Cambiamos 'id' por 'ot_number' para que sea más profesional
    list_display = ('ot_number', 'customer', 'status', 'order_type', 'branch', 'deadline')
    list_filter = ('status', 'order_type', 'branch')
    search_fields = ('ot_number', 'customer__name')
    
    # IMPORTANTE: Aquí unimos todos los bloques en la visual de la OT
    inlines = [
        OrderItemInline, 
        CardSpecificationInline, 
        TicketSpecificationInline, 
        ProductionLogInline
    ]

    # --- ACCIONES ---
    actions = ['make_ready_action', 'make_cancelled_action']

    @admin.action(description="Aprobar para Producción (Descuenta Stock)")
    def make_ready_action(self, request, queryset):
        for order in queryset:
            try:
                order.approve_for_production()
                self.message_user(request, f"OT-{order.ot_number} aprobada y stock descontado.")
            except ValidationError as e:
                self.message_user(request, f"Error en OT-{order.ot_number}: {e.message}", messages.ERROR)

    @admin.action(description="Cancelar Orden (Devuelve Stock)")
    def make_cancelled_action(self, request, queryset):
        for order in queryset:
            order.cancel_order()
            self.message_user(request, f"OT-{order.ot_number} cancelada y stock devuelto.")

    # --- PERMISOS Y ROLES ---
    def has_add_permission(self, request):
        return request.user.role in ['ADMIN', 'MANAGEMENT']

    def get_readonly_fields(self, request, obj=None):
        # Si es un operario, bloqueamos los campos sensibles
        if request.user.role == 'OPERATOR':
            return ('ot_number', 'customer', 'branch', 'order_type', 'created_by', 'deadline', 'created_at', 'total_quantity')
        return ('created_at', 'created_by')

    # --- LÓGICA AL GUARDAR ---
    def save_model(self, request, obj, form, change):
        if not change: # Si es nueva
            obj.created_by = request.user
        
        # Trazabilidad automática de estados
        if obj.status == 'PROGRESS' and not getattr(obj, 'started_at', None):
            obj.started_at = timezone.now()
        
        if obj.status == 'FINISHED' and not getattr(obj, 'finished_at', None):
            obj.finished_at = timezone.now()
            
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """Lógica extra: Asignar automáticamente al operario en los Logs"""
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, ProductionLog) and not instance.operator:
                instance.operator = request.user
            instance.save()
        formset.save_m2m()