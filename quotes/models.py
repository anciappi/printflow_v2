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
