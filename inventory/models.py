from django.db import models, transaction
from django.utils import timezone
from decimal import Decimal
from tenants.models import Branch




# ---------------------------------------------------------------------------
# MATERIAL CATEGORY
# ---------------------------------------------------------------------------

class MaterialCategory(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre de la Categoría")
    description = models.TextField(blank=True, verbose_name="Descripción")
    allows_fractioning = models.BooleanField(default=False, verbose_name="Permite Fraccionamiento", help_text="Solo aplicable para bobinas que pueden dividirse en anchos menores.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Categoría de Material"
        verbose_name_plural = "Categorías de Materiales"

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# MATERIAL (Materia Prima)
# ---------------------------------------------------------------------------

class Material(models.Model):
    UNIT_CHOICES = [
        ('M', 'mts.'),
        ('M2', 'mts2.'),
        ('KG', 'kgs.'),
        ('LT', 'lts.'),
        ('UN', 'uni.'),
    ]

    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50, blank=True)
    category = models.ForeignKey(MaterialCategory, on_delete=models.PROTECT, related_name='materials', null=True, blank=True, verbose_name="Categoría")
    unit_of_measure = models.CharField(max_length=5, choices=UNIT_CHOICES, default='UN', verbose_name="Unidad de Medida base")
    
    # (LEGACY) Mantener por compatibilidad temporal
    material_type = models.CharField(max_length=20, null=True, blank=True)
    
    # Propiedades genéricas
    grammage = models.IntegerField(null=True, blank=True, verbose_name="Gramaje (g/m2)")
    
    # Dimensiones (Bobinas y Pliegos)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Ancho (cm)")
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Largo/Desarrollo (cm)")
    
    # Atributos específicos para Pliegos
    sheets_per_package = models.IntegerField(null=True, blank=True, verbose_name="Hojas por Paquete (Cerrado)")
    stack_height_cm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Espesor del Bancal/Pallet (cm)")
    package_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Peso Bulto/Bancal (Kg)")

    # Específicos magnéticos/chip
    mag_stripe_width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    technology = models.CharField(max_length=100, null=True, blank=True)
    position = models.CharField(max_length=100, null=True, blank=True)
    
    standard_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Stock Ideal")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        specs = f" | {self.width or 0}x{self.length or 0}cm" if self.width else ""
        cat = self.category.name if self.category else (self.material_type or '')
        return f"[{cat}] {self.name} {specs}"



# ---------------------------------------------------------------------------
# INVENTORY UNIT (Unidad de Stock)
# FK to purchasing.PurchaseOrder via string reference to break circular import
# ---------------------------------------------------------------------------

class InventoryUnit(models.Model):
    STATUS_CHOICES = [('AVAILABLE', 'Disponible'), ('IN_USE', 'En Uso'), ('EXHAUSTED', 'Agotado')]

    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='units')
    # String reference to purchasing to avoid circular import
    # null=True/blank=True to support imported historical stock with no purchase order
    purchase_order = models.ForeignKey(
        'purchasing.PurchaseOrder',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='inventory_units'
    )
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
        remito = self.purchase_order.remito_number if self.purchase_order else 'IMPORT'
        return f"{self.material.name} ({self.get_width()}cm) - R:{remito}-U:{self.unit_number}"

    def get_width(self):
        return self.width_override if self.width_override else self.material.width

    def fraccionar(self, ancho_a: Decimal):
        if not self.material.category or not self.material.category.allows_fractioning:
            raise ValueError("Este material no permite fraccionamiento. Verifica la categoría.")
            
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

    def fraccionar_por_largo(self, cortes: list[Decimal]):
        if not self.material.category or not self.material.category.allows_fractioning:
            raise ValueError("Este material no permite fraccionamiento. Verifica la categoría.")

        suma_cortes = sum(cortes)
        if suma_cortes <= 0:
            raise ValueError("Las longitudes a cortar deben ser mayores a 0.")
            
        if suma_cortes > self.current_quantity:
            raise ValueError(f"La suma de los cortes ({suma_cortes}) excede el largo disponible ({self.current_quantity}).")

        remanente = self.current_quantity - suma_cortes
        lotes_a_crear = list(cortes)
        if remanente > 0:
            lotes_a_crear.append(remanente)

        hijas = []
        with transaction.atomic():
            for i, largo in enumerate(lotes_a_crear, start=1):
                hija = InventoryUnit.objects.create(
                    material=self.material,
                    purchase_order=self.purchase_order,
                    unit_number=f"{self.unit_number}.L{i}",
                    branch=self.branch,
                    initial_quantity=largo,
                    current_quantity=largo,
                    width_override=self.get_width(),
                    parent_unit=self,
                    status='AVAILABLE',
                )
                hijas.append(hija)
                
            self.status = 'EXHAUSTED'
            self.current_quantity = Decimal('0')
            self.save()

        return hijas

    def deshacer_fraccionamiento(self):
        hermanas = InventoryUnit.objects.filter(parent_unit=self)
        
        if not hermanas.exists():
            raise ValueError("No hay bobinas hijas para restaurar.")

        for h in hermanas:
            if h.current_quantity < h.initial_quantity:
                raise ValueError(f"No se puede deshacer: La unidad {h.unit_number} ya tuvo consumo.")

        is_length_split = hermanas.first().unit_number.split('.')[-1].startswith('L')

        with transaction.atomic():
            if is_length_split:
                restored_quantity = sum((h.initial_quantity for h in hermanas), Decimal('0'))
            else:
                restored_quantity = hermanas.first().initial_quantity

            hermanas.delete()
            self.status = 'AVAILABLE'
            self.current_quantity = restored_quantity
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