from django import forms
from .models import WorkOrder
from tenants.models import Branch


class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = [
            'product', 'quantity', 'branch',
            'start_date', 'due_date', 'sales_rep',
            'priority', 'production_notes'
        ]
        widgets = {
            'production_notes': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_class = "w-full bg-surface-dark border border-border-default text-slate-300 text-sm rounded focus:ring-1 focus:ring-orange-500 focus:border-orange-500 block p-2.5 placeholder-slate-600"
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = base_class
