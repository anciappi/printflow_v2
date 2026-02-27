from django.db import models
from customers.models import Customer  # Importamos tu modelo de Cliente
from inventory.models import Material  # Importamos tu modelo de Material

class Product(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Activo'),
        ('INACTIVE', 'Inactivo / Obsoleto'),
        ('DRAFT', 'En Desarrollo'),
    ]

    # Identificación
    name = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    code = models.CharField(max_length=50, unique=True, verbose_name="Cód. Interno / SKU")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='products', verbose_name="Cliente")
    
    # Especificaciones Físicas (Vital para calcular consumo de stock)
    width_mm = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ancho (mm)")
    height_mm = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Alto (mm)")
    
    # Relación con Inventario (Sustrato Base)
    substrate = models.ForeignKey(
        Material, 
        on_delete=models.PROTECT, 
        verbose_name="Sustrato / Material Base",
        help_text="Material principal del cual se descontará stock."
    )

    # Detalles de Producción (Impresión)
    colors_front = models.CharField(max_length=100, blank=True, verbose_name="Colores Frente")
    colors_back = models.CharField(max_length=100, blank=True, verbose_name="Colores Dorso")
    pantone_codes = models.CharField(max_length=200, blank=True, verbose_name="Códigos Pantone")
    
    # Archivos (La "Historia Clínica")
    preview_image = models.ImageField(upload_to='products/previews/', blank=True, null=True, verbose_name="Foto Muestra")
    tech_file = models.FileField(upload_to='products/tech_files/', blank=True, null=True, verbose_name="Plano / Arte Final (PDF/AI)")
    
    # Control
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    notes = models.TextField(blank=True, verbose_name="Observaciones de Producción")

    class Meta:
        verbose_name = "Ficha Técnica"
        verbose_name_plural = "Fichas Técnicas"
        ordering = ['customer', 'name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def dimensions(self):
        return f"{self.width_mm}x{self.height_mm} mm"