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

    ORIENTATION_CHOICES = [
        ('PORTRAIT', 'Portrait (alto avanza en bobina)'),
        ('LANDSCAPE', 'Landscape (ancho avanza en bobina)'),
    ]

    # Producción y Materiales
    bocas = models.PositiveIntegerField(null=True, blank=True, verbose_name="Bocas (Poses) del Original")
    material_used = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Material Utilizado (ml)")

    # Configuración de Postura / Polímero
    layout_rows         = models.PositiveIntegerField(null=True, blank=True, verbose_name="Filas de la Postura")
    layout_cols         = models.PositiveIntegerField(null=True, blank=True, verbose_name="Columnas de la Postura")
    gap_horizontal_mm   = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Gap Horizontal entre diseños (mm)")
    gap_vertical_mm     = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Gap Vertical entre diseños (mm)")
    margin_lateral_mm   = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Margen Lateral (cada lado, mm)")
    margin_top_mm       = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Margen Superior (mm)")
    margin_bottom_mm    = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Margen Inferior (mm)")
    orientation         = models.CharField(max_length=10, choices=ORIENTATION_CHOICES, default='PORTRAIT', verbose_name="Orientación en Bobina")
    bobina_width_mm     = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Ancho de Bobina disponible (mm)", help_text="Ancho útil del rollo o máquina. Se usará para validar que la postura entre.")

    # Resultado calculado automáticamente
    estimated_material_usage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Material Estimado (metros lineales)")

    class Meta:
        verbose_name = "Orden de Trabajo"
        verbose_name_plural = "Ordenes de Trabajo"
        ordering = ['-created_at']

    def __str__(self):
        return f"OT #{self.ot_number} | {self.product.name}"

    def get_next_status_display(self):
        """Returns the display label of the next status, or None if at end of flow."""
        transitions = {
            'PENDING':         ('PREPRESS', 'Enviar a Pre-Prensa'),
            'PREPRESS':        ('PRODUCTION', 'Iniciar Producción'),
            'PRODUCTION':      ('FINISHING', 'Pasar a Terminaciones'),
            'FINISHING':       ('QUALITY_CONTROL', 'Control de Calidad'),
            'QUALITY_CONTROL': ('READY', 'Marcar como Listo'),
            'READY':           ('DELIVERED', 'Confirmar Entrega'),
        }
        result = transitions.get(self.current_status)
        return result[1] if result else None

    def calculate_material(self):
        """
        Calcula los metros lineales estimados de bobina para esta OT.
        Retorna el valor en metros (Decimal) o None si faltan datos.
        
        Fórmula (en mm):
          bobina avanza en la dirección del 'largo' del producto.
          PORTRAIT: largo = height_mm, ancho_producto = width_mm
          LANDSCAPE: largo = width_mm, ancho_producto = height_mm

          largo_postura = (filas × largo) + ((filas-1) × gap_v) + margen_sup + margen_inf
          bocas_totales = filas × columnas
          pasadas       = ceil(cantidad / bocas_totales)
          metros        = pasadas × largo_postura / 1000
        """
        from math import ceil
        from decimal import Decimal

        required = [
            self.layout_rows, self.layout_cols, self.quantity,
            self.gap_vertical_mm, self.margin_top_mm, self.margin_bottom_mm,
        ]
        if any(v is None for v in required):
            return None
        try:
            product = self.product
        except Exception:
            return None

        if self.orientation == 'LANDSCAPE':
            largo_mm = Decimal(str(product.width_mm))
        else:
            largo_mm = Decimal(str(product.height_mm))

        filas   = Decimal(self.layout_rows)
        gap_v   = Decimal(str(self.gap_vertical_mm))
        m_top   = Decimal(str(self.margin_top_mm))
        m_bot   = Decimal(str(self.margin_bottom_mm))

        largo_postura = (filas * largo_mm) + ((filas - 1) * gap_v) + m_top + m_bot
        bocas_totales = self.layout_rows * self.layout_cols
        pasadas       = ceil(self.quantity / bocas_totales)
        metros        = (Decimal(pasadas) * largo_postura) / Decimal('1000')
        return metros.quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        # Generar número de OT atómicamente para prevenir condiciones de carrera
        if not self.ot_number:
            with transaction.atomic():
                last_order = WorkOrder.objects.select_for_update().order_by('id').last()
                new_id = (last_order.id + 1) if last_order else 1
                self.ot_number = f"OT-{timezone.now().year}-{new_id:04d}"

        # Auto-calcular material estimado si hay datos de postura
        resultado = self.calculate_material()
        if resultado is not None:
            self.estimated_material_usage = resultado
            if self.layout_rows and self.layout_cols:
                self.bocas = self.layout_rows * self.layout_cols

        super().save(*args, **kwargs)

class WorkOrderLog(models.Model):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='logs', verbose_name="Orden de Trabajo")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='work_order_logs', verbose_name="Usuario")
    status = models.CharField(max_length=20, choices=WorkOrder.STATUS_CHOICES, verbose_name="Etapa")
    quantity_produced = models.PositiveIntegerField(null=True, blank=True, verbose_name="Cantidad Parcial Producción")
    bocas = models.PositiveIntegerField(null=True, blank=True, verbose_name="Bocas (Poses)")
    material_used = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Material Utilizado (ml)")
    comment = models.TextField(blank=True, verbose_name="Observaciones / Novedad")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registro de Producción"
        verbose_name_plural = "Registros de Producción"
        ordering = ['-created_at']

    def __str__(self):
        return f"Log OT {self.work_order.ot_number} - {self.get_status_display()}"