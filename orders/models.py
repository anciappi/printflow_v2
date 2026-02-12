from django.db import models, transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from customers.models import Customer
from inventory.models import Branch, Material, InventoryUnit

class Order(models.Model):
    class Status(models.TextChoices):
        WAITING = 'WAITING', 'Ingresada - En espera de materia prima'
        READY = 'READY', 'Ingresada - Lista para producción'
        PROGRESS = 'PROGRESS', 'En Producción'
        FINISHED = 'FINISHED', 'Finalizado'
        DELIVERED = 'DELIVERED', 'Entregado'
        CANCELLED = 'CANCELLED', 'Cancelado'

    class OrderType(models.TextChoices):
        CARDS = 'CARDS', 'Tarjetas'
        TIKETS = 'TICKETS', 'Tickets'

    # --- CAMPOS BASE ---
    ot_number = models.CharField(max_length=20, unique=True, verbose_name="Nº OT")
    order_type = models.CharField(max_length=10, choices=OrderType.choices, default=OrderType.CARDS)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Cliente")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name="Sucursal de Producción")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WAITING)
    total_quantity = models.PositiveIntegerField(verbose_name="Cantidad Total Pedida")
    quantity_delivered = models.PositiveIntegerField(default=0, verbose_name="Cantidad Entregada")
    created_at = models.DateField(auto_now_add=True)
    deadline = models.DateField(verbose_name="Fecha de Entrega Prometida")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_orders')

    def __str__(self):
        return f"{self.ot_number} | {self.customer.name}"

    # --- LÓGICA DE STOCK ---
    def approve_for_production(self):
        """Reserva el stock al aprobar la OT"""
        if self.status != self.Status.WAITING:
            return 

        with transaction.atomic():
            for item in self.items.all():
                stock_record = InventoryUnit.objects.filter(
                    branch=self.branch, 
                    material=item.material
                ).first()

                if not stock_record or stock_record.quantity < item.estimated_quantity:
                    raise ValidationError(
                        f"Stock insuficiente de {item.material.name} en {self.branch.name}."
                    )

                stock_record.quantity -= item.estimated_quantity
                stock_record.save()

            self.status = self.Status.READY
            self.save()

    def cancel_order(self):
        """Devuelve el stock si se cancela la OT"""
        if self.status in [self.Status.READY, self.Status.PROGRESS]:
            with transaction.atomic():
                for item in self.items.all():
                    stock_record, _ = InventoryUnit.objects.get_or_create(
                        branch=self.branch, 
                        material=item.material
                    )
                    stock_record.quantity += item.estimated_quantity
                    stock_record.save()
                
                self.status = self.Status.CANCELLED
                self.save()

# --- MODELOS DE ESPECIFICACIÓN ---

class CardSpecification(models.Model):
    """Campos para Magtick"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='card_spec')
    chip_location = models.CharField(max_length=5, choices=[('A','A'),('B','B'),('C','C'),('D','D')], blank=True)
    overlay_f_d = models.CharField(max_length=100, blank=True)
    pvc_f_d = models.CharField(max_length=100, blank=True)
    inlay = models.CharField(max_length=100, blank=True)
    band_coercivity = models.CharField(max_length=50, blank=True)
    temp_soldado_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temp_soldado_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

class TicketSpecification(models.Model):
    """Campos para Velton"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='ticket_spec')
    bocas_por_pliego = models.PositiveIntegerField(default=1)
    demasia_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    largo_ticket_m = models.DecimalField(max_digits=10, decimal_places=4, default=0.1397)
    
    def get_meters_needed(self):
        total_with_waste = self.order.total_quantity * (1 + (self.demasia_percent / 100))
        return (total_with_waste / self.bocas_por_pliego) * self.largo_ticket_m

# --- CONSUMO DE MATERIAL Y TRAZABILIDAD ---

class OrderItem(models.Model):
    """Materiales vinculados a la OT"""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    estimated_quantity = models.DecimalField(max_digits=12, decimal_places=2)

class ProductionLog(models.Model):
    order = models.ForeignKey(Order, related_name='logs', on_delete=models.CASCADE)
    stage = models.CharField(
        max_length=50, 
        choices=[
            ('IMPRESION', 'Impresión'),
            ('ARMADO', 'Armado'),
            ('LAMINADO', 'Laminado'),
            ('CORTE', 'Corte'),
            ('PERSO', 'Personalización'),
            ('EMBALAJE', 'Embalaje'),
        ],
        verbose_name="Etapa del Proceso"
    )
    good_units = models.PositiveIntegerField(default=0, verbose_name="Unidades Buenas")
    bad_units = models.PositiveIntegerField(default=0, verbose_name="Unidades Malas/Sobra")
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def waste_percentage(self):
        total = self.good_units + self.bad_units
        if total > 0:
            return (self.bad_units / total) * 100
        return 0

    def __str__(self):
        return f"{self.stage} - OT {self.order.ot_number}"

class DeliveryNote(models.Model):
    """Remitos de entregas parciales"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='deliveries')
    remito_number = models.CharField(max_length=20, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    quantity_shipped = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            # Actualizamos la OT
            self.order.quantity_delivered += self.quantity_shipped
            if self.order.quantity_delivered >= self.order.total_quantity:
                self.order.status = Order.Status.DELIVERED
            self.order.save()