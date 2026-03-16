from django.db import models, transaction
from django.utils import timezone
from users.models import User       # Tu modelo de usuario
from products.models import Product # El modelo que acabamos de crear
from tenants.models import Branch

class WorkOrder(models.Model):
    # Estados del Flujo de Trabajo (Workflow)
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente Planificación'),
        ('PREPRESS', 'Pre-Prensa / Diseño'),
        ('PRODUCTION', 'En Producción'),
        ('FINISHING', 'Terminaciones / Corte'),
        ('QUALITY_CONTROL', 'Control de Calidad'),
        ('READY', 'Listo para Entrega'),
        ('DELIVERED', 'Entregado'),
        ('CANCELLED', 'Anulada'),
    ]

    PRIORITY_CHOICES = [
        ('NORMAL', 'Normal'),
        ('HIGH', 'Alta'),
        ('URGENT', 'Urgente (Rush)'),
    ]

    # Cabecera
    ot_number = models.CharField(max_length=20, unique=True, verbose_name="N° Orden (OT)")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders', verbose_name="Producto Solicitado")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad Solicitada")
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True, verbose_name="Inicio Programado")
    due_date = models.DateField(verbose_name="Fecha de Entrega Prometida")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="Finalizado Real")

    # Responsables y Estado
    sales_rep = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sales_orders', verbose_name="Vendedor")
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL')
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='work_orders',
        verbose_name="Branch"
    )
    
    # Notas específicas de ESTA orden (ej: "El cliente pidió cambiar el rojo por azul solo en esta tirada")
    production_notes = models.TextField(blank=True, verbose_name="Notas de Orden")

    # Campos calculados (se llenarán al guardar)
    estimated_material_usage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Metros lineales estimados a consumir")

    class Meta:
        verbose_name = "Orden de Trabajo"
        verbose_name_plural = "Ordenes de Trabajo"
        ordering = ['-created_at']

    def __str__(self):
        return f"OT #{self.ot_number} | {self.product.name}"

    def save(self, *args, **kwargs):
        # Generar número de OT atómicamente para prevenir condiciones de carrera
        if not self.ot_number:
            with transaction.atomic():
                last_order = WorkOrder.objects.select_for_update().order_by('id').last()
                new_id = (last_order.id + 1) if last_order else 1
                self.ot_number = f"OT-{timezone.now().year}-{new_id:04d}"
        super().save(*args, **kwargs)