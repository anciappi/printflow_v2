from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderItem, CardSpecification, TicketSpecification, ProductionLog, Product

# Estilos Tailwind (Los mismos del inventario)
INPUT_CLASSES = "w-full bg-[#0f1115] border border-[#2d333b] text-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors rounded-sm"
SELECT_CLASSES = "w-full bg-[#0f1115] border border-[#2d333b] text-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors rounded-sm appearance-none"
CHECKBOX_CLASSES = "w-4 h-4 text-blue-600 bg-[#0f1115] border-[#2d333b] rounded focus:ring-blue-500 focus:ring-2"


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        # AHORA PEDIMOS PRODUCTO EN VEZ DE CLIENTE
        fields = ['product', 'total_quantity', 'deadline'] 
        widgets = {
            'product': forms.Select(attrs={'class': SELECT_CLASSES}), # Nuevo campo
            'total_quantity': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'deadline': forms.DateInput(attrs={'class': INPUT_CLASSES, 'type': 'date'}),
        }
        labels = {
            'product': 'Seleccionar Producto (Ficha Técnica)',
            'deadline': 'Fecha de Entrega',
            'total_quantity': 'Cantidad a Producir'
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['material', 'estimated_quantity']
        widgets = {
            'material': forms.Select(attrs={'class': SELECT_CLASSES}),
            'estimated_quantity': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Cant. Estimada'}),
        }

# Formset para agregar múltiples materiales a la vez
OrderItemFormSet = inlineformset_factory(
    Order, OrderItem, form=OrderItemForm,
    extra=1, can_delete=True
)

class CardSpecForm(forms.ModelForm):
    class Meta:
        model = CardSpecification
        exclude = ['order']
        widgets = {
            'chip_location': forms.Select(attrs={'class': SELECT_CLASSES}),
            'overlay_f_d': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'pvc_f_d': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'inlay': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'band_coercivity': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'temp_soldado_max': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'temp_soldado_min': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
        }

class ProductionLogForm(forms.ModelForm):
    class Meta:
        model = ProductionLog
        fields = ['stage', 'good_units', 'bad_units']
        widgets = {
            'stage': forms.Select(attrs={'class': SELECT_CLASSES}),
            'good_units': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'bad_units': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'code': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'customer': forms.Select(attrs={'class': SELECT_CLASSES}),
            'product_type': forms.Select(attrs={'class': SELECT_CLASSES}),
            'laminate_finish': forms.Select(attrs={'class': SELECT_CLASSES}),
            'magstripe_type': forms.Select(attrs={'class': SELECT_CLASSES}),
            'chip_type': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'units_per_box': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            # Las imágenes usan el input de archivo estándar
        }