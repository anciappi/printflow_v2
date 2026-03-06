from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product
from .forms import ProductForm
from customers.models import Customer

class ProductCatalogView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'products/product_catalog.html'
    context_object_name = 'customers'

    def get_queryset(self):
        # Obtenemos clientes que tengan al menos un producto activo
        # Ordenamos por nombre para que la lista sea fácil de navegar
        return Customer.objects.filter(products__isnull=False).distinct().prefetch_related('products').order_by('name')

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:catalog')

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:catalog')

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:catalog')
