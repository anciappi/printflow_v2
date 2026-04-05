from django import forms
from .models import Customer

INPUT_CLASS = (
    "w-full bg-[#0f1115] border border-[#2d333b] text-slate-300 text-sm rounded "
    "focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 placeholder-slate-600"
)

FISCAL_FIELDS = [
    'street', 'street_number', 'floor_apt', 'zip_code', 'city', 'province', 'country',
]
DELIVERY_FIELDS = [
    'delivery_street', 'delivery_street_number', 'delivery_floor_apt',
    'delivery_zip_code', 'delivery_city', 'delivery_province', 'delivery_country',
]


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'name', 'customer_type', 'tax_id',
            'email', 'phone',
            *FISCAL_FIELDS,
            'delivery_same_as_fiscal',
            *DELIVERY_FIELDS,
            'assigned_to', 'is_active', 'notes',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = (
                    "w-4 h-4 text-emerald-600 bg-gray-100 border-gray-300 "
                    "rounded focus:ring-emerald-500 focus:ring-2 cursor-pointer"
                )
                continue
            field.widget.attrs['class'] = INPUT_CLASS
