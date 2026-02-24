from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.utils import timezone
from inventory.models import Material, Branch

# 1. CLIENTES
class Customer(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Razón Social")
    code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Código Interno")
    def __str__(self): return self.name

# 2. PRODUCTO (FICHA TÉCNICA MAESTRA)
class Product(models.Model):
    PRODUCT_TYPES = [
        ('CARD', '💳 Tarjeta Plástica / Magnética'),
        ('TICKET', '🎟️ Ticket / Entrada'),
        ('OTHER', '📦 Otro'),
    ]
    # Identificación
    code = models.CharField(max_length=50, unique=True, verbose_name="Cód. Producto / SKU")
    name = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Cliente")
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPES, default='CARD', verbose_name="Tipo")
    
    # Imágenes
    image_front = models.ImageField(upload_to='products/front/', null=True, blank=True, verbose_name="Imagen Anverso")
    image_back = models.ImageField(upload_to='products/back/', null=True, blank=True, verbose_name="Imagen Reverso")
    
    # Especificaciones Técnicas (Checkboxes)
    has_uv = models.BooleanField(default=False, verbose_name="Lleva UV")
    has_laminating = models.BooleanField(default=True, verbose_name="Lleva Laminado")
    laminate_finish = models.CharField(max_length=20, choices=[('GLOSS', 'Brillante'), ('MATTE', 'Mate')], default='GLOSS', blank=True)
    
    has_magstripe = models.BooleanField(default=False, verbose_name="Banda Magnética")
    magstripe_type = models.CharField(max_length=10, choices=[('LOCO', 'Lo-Co'), ('HICO', 'Hi-Co')], blank=True)
    
    has_chip = models.BooleanField(default=False, verbose_name="Lleva Chip")
    chip_type = models.CharField(max_length=50, blank=True, verbose_name="Tipo de Chip")
    
    has_contactless = models.BooleanField(default=False, verbose_name="Antena / Inlay")
    has_hologram = models.BooleanField(default=False, verbose_name="Holograma")
    has_signature_panel = models.BooleanField(default=False, verbose_name="Panel de Firma")
    has_stamping = models.BooleanField(default=False, verbose_name="Stamping")
    has_variable_data = models.BooleanField(default=False, verbose_name="Dato Variable")
    
    units_per_box = models.PositiveIntegerField(default=500, verbose_name="Unidades por Caja")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self): return f"{self.code} - {self.name}"

# 3. ORDEN DE TRABAJO
class Order(models.Model):
    STATUS_CHOICES = [
        ('WAITING', '⏳ Esperando Material'),
        ('READY', '📦 Lista para Producción'),
        ('PROGRESS', '⚙️ En Producción'),
        ('FINISHED', '✅ Finalizada'),
        ('DELIVERED', '🚚 Entregada'),
        ('CANCELED', '❌ Cancelada'),
    ]

    ot_number = models.CharField(max_length=20, unique=True, verbose_name="Nº OT")
    # Vinculamos al Producto, NO al cliente directo
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Producto (Ficha Técnica)")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name="Sucursal Producción")
    
    total_quantity = models.PositiveIntegerField(verbose_name="Cantidad a Producir")
    quantity_delivered = models.PositiveIntegerField(default=0)
    
    deadline = models.DateField(verbose_name="Fecha Entrega")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WAITING')

    def __str__(self): return self.ot_number

# 4. MATERIALES REQUERIDOS POR LA OT
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    estimated_quantity = models.DecimalField(max_digits=12, decimal_places=2)

# 5. LOG DE AVANCE
class ProductionLog(models.Model):
    order = models.ForeignKey(Order, related_name='logs', on_delete=models.CASCADE)
    stage = models.CharField(max_length=50, choices=[
        ('IMPRESION', 'Impresión'), ('ARMADO', 'Armado'), ('LAMINADO', 'Laminado'),
        ('CORTE', 'Corte'), ('PERSO', 'Personalización'), ('EMBALAJE', 'Embalaje')
    ])
    good_units = models.PositiveIntegerField(default=0)
    bad_units = models.PositiveIntegerField(default=0)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ProductMaterial(models.Model):
    """
    Receta Estándar (Bill of Materials).
    Define qué materiales y en qué cantidad se usan para fabricar 1 unidad de este producto.
    """
    product = models.ForeignKey(Product, related_name='standard_materials', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.PROTECT, verbose_name="Material Estándar")
    
    # Ej: Para 1 tarjeta usas 0.1 pliegos (si entran 10 en el pliego)
    quantity_per_unit = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Consumo por Unidad")
    
    def __str__(self):
        return f"{self.material.name} ({self.quantity_per_unit})"