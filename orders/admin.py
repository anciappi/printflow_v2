from django.contrib import admin
from .models import Customer, Product, Order, OrderItem, ProductionLog

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('ot_number', 'get_product', 'status', 'deadline')
    inlines = [OrderItemInline]
    def get_product(self, obj): return obj.product.name

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(ProductionLog)