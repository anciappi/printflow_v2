from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class PrintShop(TenantMixin):
    """
    Represents a print shop tenant (a 'floor' in the building analogy).
    Each PrintShop gets its own isolated PostgreSQL schema.
    """
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    name = models.CharField(max_length=100)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='basic')
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

    auto_create_schema = True

    class Meta:
        verbose_name = 'Print Shop'
        verbose_name_plural = 'Print Shops'

    def __str__(self):
        return f"{self.name} ({self.schema_name})"


class Domain(DomainMixin):
    """
    Represents a subdomain associated with a PrintShop tenant.
    Example: velton.printflow.com → schema: velton
    """
    class Meta:
        verbose_name = 'Domain'
        verbose_name_plural = 'Domains'


class Branch(models.Model):
    """
    Represents a business unit within a tenant (a 'department' in the building analogy).
    Example: Velton and Magtik are both branches of Grupo Velton (the tenant).
    """
    tenant = models.ForeignKey(
        PrintShop,
        on_delete=models.CASCADE,
        related_name='branches'
    )
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Branch'
        verbose_name_plural = 'Branches'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.tenant.name})"
