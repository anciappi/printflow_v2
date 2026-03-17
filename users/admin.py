from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'tenant', 'is_staff', 'is_active']
    list_filter = ['role', 'tenant', 'is_staff']
    search_fields = ['username', 'email']

    fieldsets = UserAdmin.fieldsets + (
        ('PrintFlow', {
            'fields': ('role', 'phone', 'avatar', 'tenant')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('PrintFlow', {
            'fields': ('role', 'phone', 'tenant')
        }),
    )