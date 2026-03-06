from django import forms
from .models import WorkOrder

class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ['product', 'quantity', 'start_date', 'due_date', 'sales_rep', 'priority', 'production_notes']
