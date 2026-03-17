from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        MANAGEMENT = 'MANAGEMENT', 'Gerencia'
        DESIGNER = 'DESIGNER', 'Diseñador'
        TEAM = 'TEAM', 'Equipo'
        SALES = 'SALES', 'Vendedor/Comercial'
        PORTAL = 'PORTAL', 'Cliente Portal'

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.TEAM
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # Tenant scoping — None means superadmin (access to all tenants)
    tenant = models.ForeignKey(
        'tenants.PrintShop',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='users',
        help_text='None = superadmin with access to all tenants'
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_superadmin(self):
        """Returns True if user has access to all tenants."""
        return self.tenant is None and self.is_staff