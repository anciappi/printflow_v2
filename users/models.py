from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        MANAGEMENT = 'MANAGEMENT', 'Gerencia'
        DESIGNER = 'DESIGNER', 'Diseñador'
        TEAM = 'TEAM', 'Equipo'
        SALES = 'SALES', 'Vendedor/Comercial'
        PORTAL = 'PORTAL', 'Portal Client'

    role = models.CharField(
        max_length=20, 
        choices=Roles.choices, 
        default=Roles.TEAM
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Podemos agregar una imagen de perfil o firma digital más adelante
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"