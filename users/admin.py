from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Agregamos el campo 'role' y 'phone' a los formularios del Admin
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Imprenta', {'fields': ('role', 'phone', 'avatar')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Imprenta', {'fields': ('role', 'phone', 'avatar')}),
    )
    list_display = ['username', 'email', 'role', 'is_staff']