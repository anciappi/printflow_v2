from django.db import models, transaction
from django.utils import timezone
from decimal import Decimal
from tenants.models import Branch




# ---------------------------------------------------------------------------
# MATERIAL (Materia Prima)
# ---------------------------------------------------------------------------

class Material(models.Model):
    TYPE_CHOICES = [
        ('PAPER', 'Papel'),
        ('MAG_STRIPE', 'Banda Magnética'),
        ('PAPEL_SEMI', 'Papel Semielaborado'),
        ('PLIEGO_CHIP', 'Pliego con Chip'),
        ('ADHESIVO', 'Adhesivo'),
        ('CHIP_INLAI', 'Chip INLAI'),
        ('CARTULINA', 'Cartulina'),
        ('OTHER', 'Otros'),
    ]
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50, blank=True)
    material_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    grammage = models.IntegerField(null=True, blank=True, verbose_name="Gramaje (g/m2)")
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Ancho (cm)")
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Largo/Desarrollo (cm)")
    mag_stripe_width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    technology = models.CharField(max_length=100, null=True, blank=True)
    position = models.CharField(max_length=100, null=True, blank=True)
    standard_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    package_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Peso Bulto (Kg)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        tech = f" | {self.technology}" if self.technology else ""
        specs = f"{self.width or 0}x{self.length or 0} | {self.grammage or 0}g"
        return f"{self.get_material_type_display()} - {self.name} ({specs}{tech})"


# ---------------------------------------------------------------------------
# INVENTORY UNIT (Unidad de Stock)
# FK to purchasing.PurchaseOrder via string reference to break circular import
# ---------------------------------------------------------------------------

class InventoryUnit(models.Model):
    STATUS_CHOICES = [('AVAILABLE', 'Disponible'), ('IN_USE', 'En Uso'), ('EXHAUSTED', 'Agotado')]

    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='units')
    # String reference to purchasing to avoid circular import
    purchase_order = models.ForeignKey('purchasing.PurchaseOrder', on_delete=models.CASCADE, related_name='inventory_units')
    unit_number = models.CharField(max_length=20)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    initial_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    current_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='AVAILABLE')
    width_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    parent_unit = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['unit_number']

    def __str__(self):
        return f"{self.material.name} ({self.get_width()}cm) - R:{self.purchase_order.remito_number}-U:{self.unit_number}"

    def get_width(self):
        return self.width_override if self.width_override else self.material.width

    def fraccionar(self, ancho_a: Decimal):
        ancho_padre = self.get_width()

        if ancho_a >= ancho_padre or ancho_a <= 0:
            raise ValueError("El ancho del corte debe ser menor al ancho total y mayor a 0.")

        ancho_b = ancho_padre - ancho_a

        with transaction.atomic():
            hija_a = InventoryUnit.objects.create(
                material=self.material,
                purchase_order=self.purchase_order,
                unit_number=f"{self.unit_number}.A",
                branch=self.branch,
                initial_quantity=self.current_quantity,
                current_quantity=self.current_quantity,
                width_override=ancho_a,
                parent_unit=self,
                status='AVAILABLE',
            )
            hija_b = InventoryUnit.objects.create(
                material=self.material,
                purchase_order=self.purchase_order,
                unit_number=f"{self.unit_number}.B",
                branch=self.branch,
                initial_quantity=self.current_quantity,
                current_quantity=self.current_quantity,
                width_override=ancho_b,
                parent_unit=self,
                status='AVAILABLE',
            )
            self.status = 'EXHAUSTED'
            self.current_quantity = 0
            self.save()

        return hija_a, hija_b

    def deshacer_fraccionamiento(self):
        hermanas = InventoryUnit.objects.filter(parent_unit=self)

        for h in hermanas:
            if h.current_quantity < h.initial_quantity:
                raise ValueError(f"No se puede deshacer: La unidad {h.unit_number} ya tuvo consumo.")

        with transaction.atomic():
            hermanas.delete()
            self.status = 'AVAILABLE'
            self.current_quantity = self.initial_quantity
            self.save()


# ---------------------------------------------------------------------------
# CONSUMPTION LOG (Consumo de Materia Prima)
# ---------------------------------------------------------------------------

class ConsumptionLog(models.Model):
    inventory_unit = models.ForeignKey(InventoryUnit, on_delete=models.CASCADE, related_name='consumptions')
    quantity_used = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    responsible = models.ForeignKey('users.User', on_delete=models.PROTECT)
    reference_ot = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ref. OT")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Consumo {self.quantity_used} de {self.inventory_unit} — OT: {self.reference_ot or '—'}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            unit = self.inventory_unit
            if self.pk:
                old_val = ConsumptionLog.objects.get(pk=self.pk).quantity_used
                unit.current_quantity += (old_val - self.quantity_used)
            else:
                unit.current_quantity -= self.quantity_used
            unit.status = 'EXHAUSTED' if unit.current_quantity <= 0 else 'IN_USE'
            unit.save()
            super().save(*args, **kwargs)

    def deshacer_consumo(self):
        with transaction.atomic():
            unidad = self.inventory_unit
            unidad.current_quantity += self.quantity_used
            if unidad.status == 'EXHAUSTED' and unidad.current_quantity > 0:
                unidad.status = 'IN_USE'
            unidad.save()
            self.delete()


# ---------------------------------------------------------------------------
# MATERIAL STOCK SUMMARY (Proxy — Managerial view)
# ---------------------------------------------------------------------------

class MaterialStockSummary(Material):
    class Meta:
        proxy = True
        verbose_name = '📊 Resumen Gerencial'
        verbose_name_plural = '📊 Resumen Gerencial'