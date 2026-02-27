from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'code', 'customer', 
            'width_mm', 'height_mm', 'substrate',
            'colors_front', 'colors_back', 'pantone_codes',
            'preview_image', 'tech_file', 'notes', 'status'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'substrate': forms.Select(attrs={'class': 'bg-[#0f1115]'}), # Fondo oscuro específico para selects
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Estilo común para todos los campos
        base_class = "w-full bg-[#0f1115] border border-[#2d333b] text-slate-300 text-sm rounded focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 placeholder-slate-600"
        
        for field_name, field in self.fields.items():
            # Aplicamos la clase base
            field.widget.attrs['class'] = base_class
            
            # Ajustes específicos si es necesario
            if field_name == 'preview_image' or field_name == 'tech_file':
                field.widget.attrs['class'] = "block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-emerald-900/20 file:text-emerald-400 hover:file:bg-emerald-900/40 cursor-pointer bg-[#0f1115] border border-[#2d333b] rounded"