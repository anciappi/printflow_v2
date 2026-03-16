from django.db import models, transaction
from django.utils import timezone


# ---------------------------------------------------------------------------
# SUPPLIER
# ---------------------------------------------------------------------------

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# PURCHASE ORDER
# ---------------------------------------------------------------------------

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pendiente'), ('RECEIVED', 'Recibido')]

    remito_number = models.CharField(max_length=50, unique=True, verbose_name="Cód. Interno OC")
    vendor_remito = models.CharField(max_length=50, blank=True, null=True, verbose_name="Remito Físico Proveedor")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    # String reference to tenants.Branch (central model)
    branch = models.ForeignKey('tenants.Branch', on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    order_date = models.DateField(default=timezone.now)
    delivery_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.remito_number} — {self.supplier}"

    def mark_as_received(self):
        from inventory.models import InventoryUnit  # local import to avoid circular ref
        if self.status == 'PENDING':
            with transaction.atomic():
                for item in self.items.all():
                    for i in range(1, int(item.quantity_ordered) + 1):
                        InventoryUnit.objects.create(
                            material=item.material,
                            purchase_order=self,
                            unit_number=str(i),
                            initial_quantity=item.quantity_per_unit,
                            current_quantity=item.quantity_per_unit,
                            branch=self.branch,
                        )
                self.status = 'RECEIVED'
                self.delivery_date = timezone.now().date()
                self.save()
            return True
        return False


# ---------------------------------------------------------------------------
# PURCHASE ORDER ITEM
# ---------------------------------------------------------------------------

class PurchaseOrderItem(models.Model):
    order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    # String reference to avoid circular import
    material = models.ForeignKey('inventory.Material', on_delete=models.CASCADE)
    quantity_ordered = models.IntegerField()
    quantity_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Peso Total (Kg)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.material} x{self.quantity_ordered} (OC: {self.order.remito_number})"
