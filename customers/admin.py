from django.contrib import admin
from .models import Customer

# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer_type', 'tax_id', 'email', 'phone', 'is_active')
    list_filter = ('customer_type', 'is_active')
    search_fields = ('name', 'tax_id', 'email')
    list_editable = ('is_active',) # Permite activar/desactivar desde la lista