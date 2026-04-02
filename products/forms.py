from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'product_type', 'code', 'customer', 'status',
            'width_mm', 'height_mm', 'substrate',
            'colors_front', 'colors_back',
            'has_laminate', 'laminate_front', 'laminate_back', 'laminate_type',
            'has_varnish', 'varnish_front', 'varnish_back', 'varnish_type',
            'has_mag_stripe', 'mag_stripe_front', 'mag_stripe_back', 'mag_stripe_width', 'mag_stripe_distance_to_edge', 'mag_coercivity',
            'has_chip', 'chip_front', 'chip_back', 'chip_type',
            'has_uv_sectorizado', 'uv_front', 'uv_back',
            'has_hot_stamping', 'hot_stamping_front', 'hot_stamping_back',
            'has_holograma', 'holograma_front', 'holograma_back',
            'has_troquelado', 'troquelado_front', 'troquelado_back',
            'packaging_type', 'qty_per_box',
            'design_front', 'design_back', 'diecut_file', 'tech_file',
            'notes', 'notes_front', 'notes_back'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Notas generales del producto...'}),
            'notes_front': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Indicar detalles específicos de la impresión frontal...'}),
            'notes_back': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Indicar detalles específicos de la impresión dorso...'}),
            'substrate': forms.Select(attrs={'class': 'bg-[#0f1115]'}),
            'laminate_type': forms.Select(),
            'varnish_type': forms.Select(),
            'mag_coercivity': forms.Select(),
            'packaging_type': forms.Select(),
            
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
        config_fields = {
            'laminate_type', 'varnish_type', 'mag_coercivity',
            'mag_stripe_width', 'mag_stripe_distance_to_edge', 'chip_type'
        }

        # These fields are conditionally shown/hidden by JS toggles.
        # When the toggle is OFF the browser disables the input and it is
        # not included in the POST data. Mark them not-required so Django
        # does not raise a validation error; clean() will restore defaults.
        for field_name in config_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'w-3.5 h-3.5 text-emerald-600 bg-[#0f1115] border-[#2d333b] rounded focus:ring-emerald-500 focus:ring-1 cursor-pointer')
                continue
            if field_name in file_fields:
                # Clase ya seteada en widgets, no sobrescribir
                continue

            if field_name in config_fields:
                field.widget.attrs['class'] = (
                    "w-full bg-[#0f1115] border border-[#2d333b] text-slate-300 text-xs rounded "
                    "focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 block px-2 py-0.5 h-7 placeholder-slate-600"
                )
            else:
                field.widget.attrs['class'] = base_class

    def clean(self):
        cleaned_data = super().clean()

        # When a main toggle is OFF its config select is disabled by JS and
        # therefore absent from POST. Restore the model-level default so the
        # record is saved with a valid, meaningful value instead of ''.
        if not cleaned_data.get('has_laminate'):
            cleaned_data['laminate_type'] = cleaned_data.get('laminate_type') or 'NONE'

        if not cleaned_data.get('has_varnish'):
            cleaned_data['varnish_type'] = cleaned_data.get('varnish_type') or 'NONE'

        if not cleaned_data.get('has_mag_stripe'):
            cleaned_data['mag_coercivity'] = cleaned_data.get('mag_coercivity') or 'NONE'
            cleaned_data['mag_stripe_width'] = cleaned_data.get('mag_stripe_width') or ''
            cleaned_data['mag_stripe_distance_to_edge'] = cleaned_data.get('mag_stripe_distance_to_edge') or ''

        if not cleaned_data.get('has_chip'):
            cleaned_data['chip_type'] = cleaned_data.get('chip_type') or ''

        return cleaned_data