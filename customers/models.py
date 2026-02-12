from django.db import models


# Create your models here.
class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('INDIVIDUAL', 'Persona Física'),
        ('COMPANY', 'Empresa / Jurídica'),
    ]

    name = models.CharField(max_length=150, verbose_name="Nombre o Razón Social")
    customer_type = models.CharField(max_length=15, choices=CUSTOMER_TYPE_CHOICES, default='COMPANY')
    
    # Datos Fiscales (Ajusta el nombre 'CUIT/RUT/NIT' según tu país)
    tax_id = models.CharField(max_length=20, unique=True, verbose_name="ID Fiscal / Tax ID")
    
    # Contacto
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, verbose_name="Dirección")
    
    # Información comercial
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Un campo de notas es vital en imprentas (ej: "Suele pedir laminado mate", "Entregar en portería")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas internas")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.tax_id})"