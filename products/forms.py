from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'product_type', 'code', 'customer', 'status',
            'width_mm', 'height_mm', 'substrate',
            'colors_front', 'colors_back',
            'has_laminate', 'laminate_type',
            'has_varnish', 'varnish_type',
            'has_mag_stripe', 'mag_coercivity',
            'has_chip', 'chip_type',
            'has_uv_sectorizado', 'has_hot_stamping', 'has_holograma', 'has_troquelado',
            'packaging_type', 'qty_per_box', 'delivery_address',
            'design_front', 'design_back', 'diecut_file', 'tech_file', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'substrate': forms.Select(attrs={'class': 'bg-[#0f1115]'}),
            'laminate_type': forms.Select(),
            'varnish_type': forms.Select(),
            'mag_coercivity': forms.Select(),
            'packaging_type': forms.Select(),
            'has_laminate':       forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-emerald-600 bg-gray-100 border-gray-300 rounded focus:ring-emerald-500 focus:ring-2'}),
            'has_varnish':        forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-emerald-600 bg-gray-100 border-gray-300 rounded focus:ring-emerald-500 focus:ring-2'}),
            'has_mag_stripe':     forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-emerald-600 bg-gray-100 border-gray-300 rounded focus:ring-emerald-500 focus:ring-2'}),
            'has_chip':           forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-emerald-600 bg-gray-100 border-gray-300 rounded focus:ring-emerald-500 focus:ring-2'}),
            'has_uv_sectorizado': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-emerald-600 bg-gray-100 border-gray-300 rounded focus:ring-emerald-500 focus:ring-2'}),
            'has_hot_stamping':   forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-emerald-600 bg-gray-100 border-gray-300 rounded focus:ring-emerald-500 focus:ring-2'}),
            'has_holograma':      forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-emerald-600 bg-gray-100 border-gray-300 rounded focus:ring-emerald-500 focus:ring-2'}),
            'has_troquelado':     forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-emerald-600 bg-gray-100 border-gray-300 rounded focus:ring-emerald-500 focus:ring-2'}),
            # ClearableFileInput to support deletion, hidden as we use custom buttons
            'design_front': forms.ClearableFileInput(attrs={'id': 'id_design_front', 'class': 'hidden'}),
            'design_back':  forms.ClearableFileInput(attrs={'id': 'id_design_back',  'class': 'hidden'}),
            'diecut_file':  forms.ClearableFileInput(attrs={'id': 'id_diecut_file',  'class': 'hidden'}),
            'tech_file':    forms.ClearableFileInput(attrs={'id': 'id_tech_file',    'class': 'hidden'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_class = (
            "w-full bg-[#0f1115] border border-[#2d333b] text-slate-300 text-sm rounded "
            "focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 placeholder-slate-600"
        )

        file_fields = {'design_front', 'design_back', 'diecut_file', 'tech_file'}

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'w-4 h-4 text-emerald-600 bg-gray-100 border-gray-300 rounded focus:ring-emerald-500 focus:ring-2 cursor-pointer')
                continue
            if field_name in file_fields:
                # Clase ya seteada en widgets, no sobrescribir
                continue
            field.widget.attrs['class'] = base_class