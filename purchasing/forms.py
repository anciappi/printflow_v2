from django import forms
from django.forms import inlineformset_factory
# Los modelos viven en inventory — purchasing los reutiliza sin mover la BD
from inventory.models import PurchaseOrder, PurchaseOrderItem, Supplier

# --- Clases de estilo (consistentes con el design system del proyecto) ---
INPUT_CLASSES = (
    "w-full bg-[#0f1115] border border-[#2d333b] text-slate-200 px-3 py-2 "
    "text-sm focus:outline-none focus:border-blue-500 transition-colors rounded-sm"
)
SELECT_CLASSES = (
    "w-full bg-[#0f1115] border border-[#2d333b] text-slate-200 px-3 py-2 "
    "text-sm focus:outline-none focus:border-blue-500 transition-colors rounded-sm appearance-none"
)


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'branch', 'customer_name', 'order_date']
        widgets = {
            'supplier':      forms.Select(attrs={'class': SELECT_CLASSES}),
            'branch':        forms.Select(attrs={'class': SELECT_CLASSES}),
            'customer_name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Opcional'}),
            'order_date':    forms.DateInput(attrs={'class': INPUT_CLASSES, 'type': 'date'}),
        }
        labels = {
            'supplier':      'Proveedor',
            'branch':        'Sucursal Destino',
            'customer_name': 'Cliente Referencia',
            'order_date':    'Fecha de Emisión',
        }


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['material', 'quantity_ordered', 'quantity_per_unit', 'total_weight']
        widgets = {
            'material':          forms.Select(attrs={'class': SELECT_CLASSES}),
            'quantity_ordered':  forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Cant.'}),
            'quantity_per_unit': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Mts/Unid'}),
            'total_weight':      forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Kg Total'}),
        }
        labels = {
            'material':          'Material',
            'quantity_ordered':  'Cant. Bobinas/Paq.',
            'quantity_per_unit': 'Cant. Mts/Uni',
            'total_weight':      'Peso Total (Kg)',
        }


PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=1,
    can_delete=True,
)


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Ej: Papelera del Sol S.A.',
            }),
        }
        labels = {'name': 'Razón Social / Nombre'}
