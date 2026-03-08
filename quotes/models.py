from django.db import models
from customers.models import Customer
from products.models import Product
from users.models import User

class QuoteRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('CONTACTED', 'Contactado'),
        ('APPROVED', 'Aprobado'),
        ('REJECTED', 'Rechazado'),
    ]

    # Prospect contact info
    requester_name = models.CharField(max_length=150)
    requester_email = models.EmailField()
    requester_phone = models.CharField(max_length=50)
    requester_cuit = models.CharField(max_length=20)

    # Billing address (who pays)
    billing_address = models.CharField(max_length=200)
    billing_city = models.CharField(max_length=100)

    # Delivery address (where work is delivered)
    same_as_billing = models.BooleanField(default=True)
    delivery_address = models.CharField(max_length=200, blank=True)
    delivery_city = models.CharField(max_length=100, blank=True)
    delivery_contact = models.CharField(max_length=150, blank=True)
    delivery_phone = models.CharField(max_length=50, blank=True)

    # Notes and files
    attached_file = models.FileField(upload_to='quotes/', blank=True, null=True)
    general_notes = models.TextField(blank=True)

    # Status flow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # On approval (null until approved)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL, related_name='quotes')
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='handled_quotes')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Solicitud de Cotización'
        verbose_name_plural = 'Solicitudes de Cotización'

    def __str__(self):
        return f"Cotización #{self.id} - {self.requester_name}"


class QuoteProduct(models.Model):
    quote = models.ForeignKey(QuoteRequest, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='quote_items')
    quantity = models.PositiveIntegerField()
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Producto de Cotización'
        verbose_name_plural = 'Productos de Cotización'

    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Cotización #{self.quote_id})"


class CardJobOrder(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Borrador'),
        ('PENDING', 'Pendiente'),
        ('IN_REVIEW', 'En Revisión'),
        ('APPROVED', 'Aprobado'),
        ('REJECTED', 'Rechazado'),
    ]

    REVIEW_CHOICES = [
        ('APPROVE', 'Aprobado para Producción'),
        ('CORRECT_RESEND', 'Corregir y Reenviar'),
        ('CORRECT_PRINT', 'Corregir y Procesar'),
    ]

    # CLIENT SECTION
    client = models.ForeignKey(QuoteRequest, null=True, blank=True, on_delete=models.SET_NULL, related_name='card_jobs')
    requester_name = models.CharField(max_length=150)
    requester_email = models.EmailField()
    requester_phone = models.CharField(max_length=50)
    requester_cuit = models.CharField(max_length=20)
    job_description = models.TextField()
    op_anterior = models.CharField(max_length=50, blank=True)
    version = models.CharField(max_length=20, blank=True)

    # COLORS
    front_colors = models.CharField(max_length=50)  # C, M, Y, K separated or code
    front_special_colors = models.TextField(blank=True)
    front_observations = models.TextField(blank=True)
    back_colors = models.CharField(max_length=50, blank=True)
    back_special_colors = models.TextField(blank=True)
    back_observations = models.TextField(blank=True)

    # TECHNICAL SPECS
    uv = models.BooleanField(default=False)
    uv_type = models.CharField(max_length=50, blank=True)
    uv_size = models.CharField(max_length=50, blank=True)
    uv_front = models.BooleanField(default=False)
    uv_back = models.BooleanField(default=False)

    antenna_inlay = models.BooleanField(default=False)
    magnetic_band = models.BooleanField(default=False)
    magnetic_band_type = models.CharField(max_length=50, blank=True)
    magnetic_band_size = models.CharField(max_length=50, blank=True)
    magnetic_band_back = models.BooleanField(default=False)

    lamination = models.BooleanField(default=False)
    lamination_type = models.CharField(max_length=50, blank=True)
    lamination_front = models.BooleanField(default=False)
    lamination_back = models.BooleanField(default=False)

    signature_panel = models.BooleanField(default=False)
    hologram = models.BooleanField(default=False)
    stamping = models.BooleanField(default=False)
    chip = models.BooleanField(default=False)
    pre_perso = models.BooleanField(default=False)
    variable_data = models.BooleanField(default=False)

    # REVIEW RESULT
    review_result = models.CharField(max_length=20, choices=REVIEW_CHOICES, blank=True)

    # APPROVAL
    approved_by = models.CharField(max_length=100, blank=True)
    approval_date = models.DateField(null=True, blank=True)

    # STATUS
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

    # Internal reference
    order_number = models.CharField(max_length=50, blank=True)
    bin_number = models.CharField(max_length=50, blank=True)
    pif_rpp = models.CharField(max_length=50, blank=True)
    ica_number = models.CharField(max_length=50, blank=True)

    # Timestamps & Meta
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='card_orders')
    attached_file = models.FileField(upload_to='card_jobs/', blank=True, null=True)
    general_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Orden de Trabajo de Tarjetas'
        verbose_name_plural = 'Órdenes de Trabajo de Tarjetas'

    def __str__(self):
        return f"Tarjetas: {self.job_description[:30]} ({self.requester_name})"
