from django import forms
from .models import WorkOrder

class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ['product', 'quantity', 'start_date', 'due_date', 'sales_rep', 'priority', 'production_notes']
        widgets = {
            'production_notes': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_class = "w-full bg-[#0f1115] border border-[#2d333b] text-slate-300 text-sm rounded focus:ring-1 focus:ring-orange-500 focus:border-orange-500 block p-2.5 placeholder-slate-600"
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = base_class
