from django import forms
from django.urls import reverse_lazy
from .models import WorkOrder
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
        else:
            # New form loading for the first time
            self.fields['product'].queryset = Product.objects.none()
