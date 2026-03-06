from django import forms
from django.forms import inlineformset_factory
from .models import Material
from purchasing.models import PurchaseOrder, PurchaseOrderItem, Supplier

# --- Clases de estilo Tailwind ---
INPUT_CLASSES = "w-full bg-[#0f1115] border border-[#2d333b] text-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors rounded-sm"
SELECT_CLASSES = "w-full bg-[#0f1115] border border-[#2d333b] text-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors rounded-sm appearance-none"

# Formulario Ordenes de trabajo
class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'branch', 'customer_name', 'order_date']
        widgets = {
            'remito_number': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ej: 0001-12345678'}),
            'supplier': forms.Select(attrs={'class': SELECT_CLASSES}),
            'branch': forms.Select(attrs={'class': SELECT_CLASSES}),
            'customer_name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Opcional'}),
            'order_date': forms.DateInput(attrs={'class': INPUT_CLASSES, 'type': 'date'}),
        }
        labels = {
            'remito_number': 'Nº Remito / OC',
            'supplier': 'Proveedor',
            'branch': 'Sucursal Destino',
            'customer_name': 'Cliente Referencia',
            'order_date': 'Fecha de Emisión',
        }

# Formulario materia prima
class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['material', 'quantity_ordered', 'quantity_per_unit', 'total_weight']
        widgets = {
            'material': forms.Select(attrs={'class': SELECT_CLASSES}),
            'quantity_ordered': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Cant.'}),
            'quantity_per_unit': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Mts/Unid'}),
            'total_weight': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Kg Total'}),
        }

# --- LA MAGIA: El FormSet ---
# Esto permite gestionar múltiples ítems dentro del mismo formulario padre
PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder, 
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=1,       # Cuántas filas vacías mostrar al inicio
    can_delete=True # Permitir borrar filas
)

# Formulario proveedor
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ej: Papelera del Sol S.A.'}),
        }
        labels = {'name': 'Razón Social / Nombre'}

# Formulario materiales
class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = [
            'name', 'brand', 'material_type', 'standard_quantity', # Info Básica
            'width', 'length', 'grammage', 'package_weight', # Dimensiones
            'technology', 'position', 'mag_stripe_width' # Tecnología
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ej: termoticket kls ff 166'}),
            'brand': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ej: Mitsbishi'}),
            'material_type': forms.Select(attrs={'class': SELECT_CLASSES}),
            'standard_quantity': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            
            # Dimensiones
            'width': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'cm'}),
            'length': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'mts'}),
            'grammage': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'g/m2'}),
            'package_weight': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Kg'}),
            
            # Chips / Bandas
            'technology': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ej: HICO'}),
            'position': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ej: Central' }),
            'mag_stripe_width': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ej: 5'}),
        }
        labels = {
            'name': 'Tipo material',
            'material_type': 'Categoría',
            'standard_quantity': 'Stock Mínimo Ideal',
            'width': 'Ancho (cm)',
            'length': 'Largo (mts)',
            'grammage': 'Gramaje',
            'technology': 'Coercitiv',
        }