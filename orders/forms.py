from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderItem, Product, ProductionLog, ProductMaterial

INPUT_CLASSES = "w-full bg-[#0f1115] border border-[#2d333b] text-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors rounded-sm"
SELECT_CLASSES = "w-full bg-[#0f1115] border border-[#2d333b] text-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors rounded-sm appearance-none"

# --- FORMULARIO DE FICHA TÉCNICA (PRODUCTO) ---
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
        }

# --- FORMULARIO DE ORDEN DE TRABAJO ---
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'branch', 'total_quantity', 'deadline']
        widgets = {
            'product': forms.Select(attrs={'class': SELECT_CLASSES}),
            'branch': forms.Select(attrs={'class': SELECT_CLASSES}),
            'total_quantity': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'deadline': forms.DateInput(attrs={'class': INPUT_CLASSES, 'type': 'date'}),
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['material', 'estimated_quantity']
        widgets = {
            'material': forms.Select(attrs={'class': SELECT_CLASSES}),
            'estimated_quantity': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
        }

OrderItemFormSet = inlineformset_factory(
    Order, OrderItem, form=OrderItemForm, extra=1, can_delete=True
)

class ProductionLogForm(forms.ModelForm):
    class Meta:
        model = ProductionLog
        fields = ['stage', 'good_units', 'bad_units']
        widgets = {
            'stage': forms.Select(attrs={'class': SELECT_CLASSES}),
            'good_units': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'bad_units': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
        }

class ProductMaterialForm(forms.ModelForm):
    class Meta:
        model = ProductMaterial
        fields = ['material', 'quantity_per_unit']
        widgets = {
            'material': forms.Select(attrs={'class': SELECT_CLASSES}),
            'quantity_per_unit': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'step': '0.0001'}),
        }

# Formset para la Receta
ProductMaterialFormSet = inlineformset_factory(
    Product, ProductMaterial, form=ProductMaterialForm, extra=1, can_delete=True
)