from django.contrib import admin
from .models import PrintShop, Domain, Branch


@admin.register(PrintShop)
class PrintShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'schema_name', 'plan', 'is_active', 'created_at']
    list_filter = ['plan', 'is_active']
    search_fields = ['name', 'schema_name']


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'is_primary']
    search_fields = ['domain']


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'is_active', 'created_at']
    list_filter = ['tenant', 'is_active']
    search_fields = ['name']
