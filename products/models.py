from django.db import models
from customers.models import Customer  # Importamos tu modelo de Cliente
from inventory.models import Material  # Importamos tu modelo de Material

# 1. Modelo para Colores (Para biblioteca futura)
class Color(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nombre Color")
    code = models.CharField(max_length=20, blank=True, verbose_name="Código (Hex/Pantone)")
    is_standard = models.BooleanField(default=False, verbose_name="Es CMYK/Estándar")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Product(models.Model):
    STATUS_CHOICES = [('ACTIVE', 'Activo'), ('INACTIVE', 'Obsoleto'), ('DRAFT', 'Borrador')]
    
    # --- Identificación ---
    PRODUCT_TYPE_CHOICES = [
        ('TARJETA', 'Tarjeta'),
        ('VOTO', 'Voto'),
        ('TICKET', 'Ticket'),
    ]
    name = models.CharField(max_length=200, verbose_name="Nombre")
    product_type = models.CharField(
        max_length=20, 
        choices=PRODUCT_TYPE_CHOICES, 
        default='TARJETA',
        verbose_name="Tipo de Producto"
    )
    code = models.CharField(max_length=50, unique=True, verbose_name="SKU")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='products')
    
    # --- Dimensiones y Sustrato ---
    width_mm = models.DecimalField(max_digits=10, decimal_places=2)
    height_mm = models.DecimalField(max_digits=10, decimal_places=2)
    substrate = models.ForeignKey(Material, on_delete=models.PROTECT, limit_choices_to={'material_type__in': ['PAPER', 'CARTULINA', 'ADHESIVO', 'PLIEGO_CHIP']})

    # --- 2. Colores (Many to Many) ---
    colors_front = models.ManyToManyField(Color, related_name='products_front', blank=True, verbose_name="Colores Frente")
    colors_back = models.ManyToManyField(Color, related_name='products_back', blank=True, verbose_name="Colores Dorso")

    # --- 3. Terminaciones (Checkboxes + Detalles) ---
    # Laminado
    LAMINATE_CHOICES = [
        ('NONE', 'Sin Laminado'),
        ('MATE', 'Mate'),
        ('GLOSSY', 'Brillante'),
        ('SOFT_TOUCH', 'Soft Touch'),
    ]
    has_laminate = models.BooleanField(default=False, verbose_name="Laminado")
    laminate_type = models.CharField(
        max_length=50, 
        choices=LAMINATE_CHOICES,
        default='NONE',
        verbose_name="Tipo Laminado"
    )

    # Barniz
    VARNISH_CHOICES = [
        ('NONE', 'Ninguno'),
        ('MATE', 'Mate'),
        ('GLOSSY', 'Brillante'),
        ('SEMI_MATE', 'Semi Mate'),
    ]
    has_varnish = models.BooleanField(default=False, verbose_name="Barniz")
    varnish_type = models.CharField(
        max_length=50,
        choices=VARNISH_CHOICES,
        default='NONE',
        verbose_name="Tipo Barniz"
    )
    
    # Banda Magnética
    MAG_STRIPE_CHOICES = [
        ('NONE', 'Sin Banda'),
        ('LOCO', 'LoCo (Baja Coercitividad)'),
        ('HICO', 'HiCo (Alta Coercitividad)'),
    ]
    has_mag_stripe = models.BooleanField(default=False, verbose_name="Banda Magnética")
    mag_coercivity = models.CharField(
        max_length=20, 
        choices=MAG_STRIPE_CHOICES, 
        default='NONE',
        verbose_name="Coercitividad"
    )
    
    # Chip / RFID
    has_chip = models.BooleanField(default=False, verbose_name="Chip / RFID")
    chip_type = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="Modelo de Chip", 
        help_text="Ejemplo: Mifare 1k, EM4100, NTAG213"
    )
    
    # Otros acabados (Checkboxes)
    has_uv_sectorizado = models.BooleanField(default=False, verbose_name="Laca UV Sectorizada")
    has_hot_stamping = models.BooleanField(default=False, verbose_name="Hot Stamping")
    has_holograma = models.BooleanField(default=False, verbose_name="Holograma")
    has_troquelado = models.BooleanField(default=False, verbose_name="Troquelado")

    # --- 4. Empaque y Logística ---
    PACKAGING_CHOICES = [
        ('CAJA_STD', 'Caja Estándar'),
        ('BOLSA', 'Bolsa Termocontraible'),
        ('INDIVIDUAL', 'Embolsado Individual'),
        ('OTRO', 'Otro (ver notas)'),
    ]
    packaging_type = models.CharField(
        max_length=100, 
        choices=PACKAGING_CHOICES, 
        default='CAJA_STD',
        verbose_name="Tipo de Empaque"
    )
    qty_per_box = models.PositiveIntegerField(verbose_name="Cantidad por Caja")

    # --- Archivos y Documentación ---
    design_front = models.FileField(upload_to='products/designs/front/', blank=True, null=True, verbose_name="Diseño Anverso (Original)")
    design_back = models.FileField(upload_to='products/designs/back/', blank=True, null=True, verbose_name="Diseño Reverso (Original)")
    diecut_file = models.FileField(upload_to='products/diecuts/', blank=True, null=True, verbose_name="Sacabocados / Plano de Corte")
    tech_file = models.FileField(upload_to='products/tech_files/', blank=True, null=True, verbose_name="Otros Adjuntos (Ficha / JPG)")
    notes = models.TextField(blank=True, verbose_name="Notas Internas")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"