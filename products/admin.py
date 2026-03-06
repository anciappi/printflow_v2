from django.contrib import admin
from .models import Product, Color

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'customer', 'status', 'created_at')
    list_filter = ('status', 'customer')
    search_fields = ('name', 'code')

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_standard')
    list_filter = ('is_standard',)
