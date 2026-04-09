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