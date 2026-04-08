from django.db import models
from django.conf import settings

# Create your models here.
class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('INDIVIDUAL', 'Persona Física'),
        ('COMPANY', 'Empresa / Jurídica'),
    ]

    name = models.CharField(max_length=150, verbose_name="Nombre o Razón Social")
    customer_type = models.CharField(max_length=15, choices=CUSTOMER_TYPE_CHOICES, default='COMPANY')
    
    # Datos Fiscales
    tax_id = models.CharField(max_length=20, unique=True, verbose_name="ID Fiscal / Tax ID")
    
    # Contacto
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    # --- Dirección Fiscal / Legal ---
    street = models.CharField(max_length=200, blank=True, verbose_name="Calle")
    street_number = models.CharField(max_length=20, blank=True, verbose_name="Número")
    floor_apt = models.CharField(max_length=50, blank=True, verbose_name="Piso / Depto")
    zip_code = models.CharField(max_length=20, blank=True, verbose_name="Código Postal")
    city = models.CharField(max_length=100, blank=True, verbose_name="Localidad / Ciudad")
    province = models.CharField(max_length=100, blank=True, verbose_name="Provincia / Estado")
    country = models.CharField(max_length=100, blank=True, default='Argentina', verbose_name="País")

    # --- Dirección de Entrega ---
    delivery_same_as_fiscal = models.BooleanField(
        default=True,
        verbose_name="Dirección de entrega igual a la fiscal"
    )
    delivery_street = models.CharField(max_length=200, blank=True, verbose_name="Calle (Entrega)")
    delivery_street_number = models.CharField(max_length=20, blank=True, verbose_name="Número (Entrega)")
    delivery_floor_apt = models.CharField(max_length=50, blank=True, verbose_name="Piso / Depto (Entrega)")
    delivery_zip_code = models.CharField(max_length=20, blank=True, verbose_name="CP (Entrega)")
    delivery_city = models.CharField(max_length=100, blank=True, verbose_name="Localidad (Entrega)")
    delivery_province = models.CharField(max_length=100, blank=True, verbose_name="Provincia (Entrega)")
    delivery_country = models.CharField(max_length=100, blank=True, default='Argentina', verbose_name="País (Entrega)")
    
    # Información comercial
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_customers')
    
    # Notas internas
    notes = models.TextField(blank=True, null=True, verbose_name="Notas internas")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.tax_id})"

    @property
    def full_delivery_address(self):
        if not self.delivery_street:
            return None
        address = f"{self.delivery_street} {self.delivery_street_number}".strip()
        if self.delivery_floor_apt:
            address += f" {self.delivery_floor_apt}"
        location = ", ".join(filter(bool, [self.delivery_city, self.delivery_province]))
        if location:
            address += f", {location}"
        return address

    def save(self, *args, **kwargs):
        if self.delivery_same_as_fiscal:
            self.delivery_street = self.street
            self.delivery_street_number = self.street_number
            self.delivery_floor_apt = self.floor_apt
            self.delivery_zip_code = self.zip_code
            self.delivery_city = self.city
            self.delivery_province = self.province
            self.delivery_country = self.country
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()