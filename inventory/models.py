from django.db import models, transaction
from django.utils import timezone
from decimal import Decimal

# Empresa
class Branch(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self): return self.name

# Proveedor
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

# Material
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

    def __str__(self):
        tech = f" | {self.technology}" if self.technology else ""
        specs = f"{self.width or 0}x{self.length or 0} | {self.grammage or 0}g"
        return f"{self.get_material_type_display()} - {self.name} ({specs}{tech})"

 #Ingrso orden de compra

#
class PurchaseOrder(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pendiente'), ('RECEIVED', 'Recibido')]
    remito_number = models.CharField(max_length=50, unique=True, verbose_name="Cód. Interno OC")
    vendor_remito = models.CharField(max_length=50, blank=True, null=True, verbose_name="Remito Físico Proveedor")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    order_date = models.DateField(default=timezone.now)
    delivery_date = models.DateField(null=True, blank=True)

    def mark_as_received(self):
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
                            branch=self.branch
                        )
                self.status = 'RECEIVED'; self.delivery_date = timezone.now().date(); self.save()
            return True
        return False

#
class PurchaseOrderItem(models.Model):
    order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity_ordered = models.IntegerField()
    quantity_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Peso Total (Kg)")

#
class InventoryUnit(models.Model):
    STATUS_CHOICES = [('AVAILABLE', 'Disponible'), ('IN_USE', 'En Uso'), ('EXHAUSTED', 'Agotado')]
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='units')
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='inventory_units')
    unit_number = models.CharField(max_length=20)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    initial_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    current_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='AVAILABLE')
    width_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    parent_unit = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    class Meta:
        ordering = ['unit_number']

    def get_width(self):
        return self.width_override if self.width_override else self.material.width

    def fraccionar(self, ancho_a: Decimal):
        ancho_padre = self.get_width()
        
        if ancho_a >= ancho_padre or ancho_a <= 0:
            raise ValueError("El ancho del corte debe ser menor al ancho total y mayor a 0.")

        ancho_b = ancho_padre - ancho_a
        
        with transaction.atomic():
            # 1. Crear Hija A
            hija_a = InventoryUnit.objects.create(
                material=self.material,
                purchase_order=self.purchase_order,
                unit_number=f"{self.unit_number}.A",
                branch=self.branch,
                initial_quantity=self.current_quantity,
                current_quantity=self.current_quantity,
                width_override=ancho_a,
                parent_unit=self,
                status='AVAILABLE'
            )
            
            # 2. Crear Hija B
            hija_b = InventoryUnit.objects.create(
                material=self.material,
                purchase_order=self.purchase_order,
                unit_number=f"{self.unit_number}.B",
                branch=self.branch,
                initial_quantity=self.current_quantity,
                current_quantity=self.current_quantity,
                width_override=ancho_b,
                parent_unit=self,
                status='AVAILABLE'
            )
            
            # 3. "Matar" a la madre (Agotada por corte)
            self.status = 'EXHAUSTED'
            self.current_quantity = 0
            self.save()
            
        return hija_a, hija_b

    def deshacer_fraccionamiento(self):
        # 1. Buscamos a todas las hermanas (todas las hijas de ese padre)
        hermanas = InventoryUnit.objects.filter(parent_unit=self)
        
        # 2. VALIDACIÓN DE SEGURIDAD
        for h in hermanas:
            if h.current_quantity < h.initial_quantity:
                raise ValueError(f"No se puede deshacer: La unidad {h.unit_number} ya tuvo consumo.")

        with transaction.atomic():
            # 3. Si están intactas, procedemos:
            hermanas.delete()
            
            # 4. Revivimos al Padre
            self.status = 'AVAILABLE'
            self.current_quantity = self.initial_quantity
            self.save()

    def __str__(self):
        return f"{self.material.name} ({self.get_width()}cm) - R:{self.purchase_order.remito_number}-U:{self.unit_number}"

#Consumo materia prima
class ConsumptionLog(models.Model):
    inventory_unit = models.ForeignKey(InventoryUnit, on_delete=models.CASCADE, related_name='consumptions')
    quantity_used = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    responsible = models.ForeignKey('users.User', on_delete=models.PROTECT)
    reference_ot = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ref. OT")

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
            # 1. Devolvemos la cantidad al stock
            unidad.current_quantity += self.quantity_used
            
            # 2. Si estaba agotada, la revivimos
            if unidad.status == 'EXHAUSTED' and unidad.current_quantity > 0:
                unidad.status = 'IN_USE' # O 'AVAILABLE'
            
            unidad.save()
            
            # 3. Borramos el registro (El crimen nunca ocurrió)
            self.delete()

#Resumen materia prima
class MaterialStockSummary(Material):
    class Meta:
        proxy = True
        verbose_name = '📊 Resumen Gerencial'
        verbose_name_plural = '📊 Resumen Gerencial'