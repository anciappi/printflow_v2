from django import forms
from django.urls import reverse_lazy
from django_tenants.utils import get_tenant
from .models import WorkOrder, WorkOrderLog
from tenants.models import Branch
from customers.models import Customer
from products.models import Product

class WorkOrderForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        required=False,
        label="Cliente"
    )

    class Meta:
        model = WorkOrder
        fields = [
            'customer', 'product', 'quantity', 'branch',
            'start_date', 'due_date', 'sales_rep',
            'priority', 'production_notes',
            # Postura / Polímero
            'orientation', 'layout_rows', 'layout_cols',
            'gap_horizontal_mm', 'gap_vertical_mm',
            'margin_lateral_mm', 'margin_top_mm', 'margin_bottom_mm',
            'bobina_width_mm', 'waste_percentage',
        ]
        widgets = {
            'production_notes': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'due_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'waste_percentage': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'Ej. 5'}),
        }

    def __init__(self, *args, **kwargs):
        # Accept request to resolve the current tenant and filter branch queryset.
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        base_class = "w-full bg-surface-dark border border-border-default text-slate-300 text-sm rounded focus:ring-1 focus:ring-orange-500 focus:border-orange-500 block p-2.5 placeholder-slate-600"

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = base_class

        if request is not None:
            current_tenant = get_tenant(request)
            self.fields['branch'].queryset = Branch.objects.filter(
                tenant=current_tenant, is_active=True
            )

        # Add HTMX triggers to the customer field
        self.fields['customer'].widget.attrs.update({
            'hx-get': reverse_lazy('orders:load_products'),
            'hx-target': '#id_product',
            'hx-on:change': 'document.getElementById("product-details-container").innerHTML = ""'
        })

        # HTMX trigger to load dynamic product details (specs, images)
        self.fields['product'].widget.attrs.update({
            'hx-get': reverse_lazy('orders:load_product_details'),
            'hx-target': '#product-details-container',
        })

        # Dynamic queryset logic for dependent dropdown
        if self.instance.pk and self.instance.product:
            # If editing an existing OT, set initial customer and product queryset
            self.fields['customer'].initial = self.instance.product.customer
            self.fields['product'].queryset = Product.objects.filter(
                customer=self.instance.product.customer,
                status='ACTIVE'
            ).order_by('name')
        elif 'customer' in self.data:
            # If form was submitted but is invalid (re-rendering)
            try:
                customer_id = int(self.data.get('customer'))
                self.fields['product'].queryset = Product.objects.filter(
                    customer_id=customer_id,
                    status='ACTIVE'
                ).order_by('name')
            except (ValueError, TypeError):
                self.fields['product'].queryset = Product.objects.none()
        elif kwargs.get('initial') and 'customer' in kwargs['initial']:
            self.fields['product'].queryset = Product.objects.filter(
                customer_id=kwargs['initial']['customer'],
                status='ACTIVE'
            ).order_by('name')
        else:
            # New form loading for the first time
            self.fields['product'].queryset = Product.objects.none()

class WorkOrderLogForm(forms.ModelForm):
    class Meta:
        model = WorkOrderLog
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'w-full bg-surface-dark border border-border-default text-white text-[11px] px-3 py-1.5 focus:border-orange-500 outline-none transition-colors rounded-sm resize-none',
                'placeholder': 'Escribí aquí observaciones, novedades o desvíos...',
                'rows': 1,
                'required': True
            }),
        }

class WorkOrderAdvanceForm(forms.ModelForm):
    class Meta:
        model = WorkOrderLog
        fields = ['production_date', 'quantity_produced', 'material_used', 'comment']
        widgets = {
            'production_date': forms.DateTimeInput(attrs={
                'class': 'w-full bg-surface-dark border border-border-default text-white text-[11px] px-3 py-1.5 focus:border-orange-500 outline-none transition-colors rounded-sm',
                'type': 'datetime-local',
                'placeholder': 'Dejar vacío para usar fecha/hora actuales',
            }),
            'quantity_produced': forms.NumberInput(attrs={
                'class': 'w-full bg-surface-dark border border-border-default text-white text-[11px] px-3 py-1.5 focus:border-orange-500 outline-none transition-colors rounded-sm',
                'placeholder': 'Cantidad',
                'min': '1',
                'required': True
            }),
            'material_used': forms.NumberInput(attrs={
                'class': 'w-full bg-surface-dark border border-border-default text-white text-[11px] px-3 py-1.5 focus:border-orange-500 outline-none transition-colors rounded-sm',
                'placeholder': 'Ej. 1500',
                'step': '1',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'w-full bg-surface-dark border border-border-default text-white text-[11px] px-3 py-1.5 focus:border-orange-500 outline-none transition-colors rounded-sm resize-none',
                'placeholder': 'Escribí aquí observaciones...',
                'rows': 2,
            }),
        }
