from django import forms
from .models import Material

# --- Clases de estilo Tailwind ---
INPUT_CLASSES = "w-full bg-[#0f1115] border border-[#2d333b] text-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors rounded-sm"
SELECT_CLASSES = "w-full bg-[#0f1115] border border-[#2d333b] text-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors rounded-sm appearance-none"

# Formulario materiales
class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = [
            'name', 'brand', 'category', 'unit_of_measure', 'standard_quantity', # Info Básica
            'width', 'length', 'grammage', 'package_weight', 'sheets_per_package', 'stack_height_cm', # Características
            'technology', 'position', 'mag_stripe_width' # Tecnología
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ej: termoticket kls ff 166'}),
            'brand': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ej: Mitsbishi'}),
            'category': forms.Select(attrs={'class': SELECT_CLASSES}),
            'unit_of_measure': forms.Select(attrs={'class': SELECT_CLASSES}),
            'standard_quantity': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            
            # Dimensiones
            'width': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'cm', 'step': '0.01'}),
            'length': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'mts/cm', 'step': '0.01'}),
            'grammage': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'g/m2'}),
            'package_weight': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Kg', 'step': '0.01'}),
            'sheets_per_package': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ej: 500'}),
            'stack_height_cm': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'cm', 'step': '0.01'}),
            
            # Chips / Bandas
            'technology': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ej: HICO'}),
            'position': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ej: Central' }),
            'mag_stripe_width': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ej: 5', 'step': '0.01'}),
        }
        labels = {
            'name': 'Nombre Identificatorio',
            'category': 'Categoría',
            'unit_of_measure': 'Unidad Base de Control',
            'standard_quantity': 'Stock Mínimo Ideal',
            'width': 'Ancho (cm)',
            'length': 'Largo / Desarrollo',
            'grammage': 'Gramaje',
            'sheets_per_package': 'Hojas x Paquete',
            'stack_height_cm': 'Espesor Bancal (cm)',
            'technology': 'Tecnología/Coercitividad',
        }