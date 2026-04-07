from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product, ProductDocument
from .forms import ProductForm
from customers.models import Customer

class ProductCatalogView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'products/product_list.html'
    context_object_name = 'customers'
    paginate_by = 20

    def get_queryset(self):
        # Obtenemos clientes que tengan al menos un producto activo
        # Ordenamos por nombre para que la lista sea fácil de navegar
        return Customer.objects.filter(products__isnull=False).distinct().prefetch_related('products').order_by('name')

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:catalog')

    def form_valid(self, form):
        response = super().form_valid(form)
        diecut_files = self.request.FILES.getlist('diecut_files_multiple')
        for f in diecut_files:
            ProductDocument.objects.create(product=self.object, file=f, doc_type='DIECUT', uploaded_by=self.request.user)
        tech_files = self.request.FILES.getlist('tech_files_multiple')
        for f in tech_files:
            ProductDocument.objects.create(product=self.object, file=f, doc_type='TECH', uploaded_by=self.request.user)
        return response

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:catalog')

    def form_valid(self, form):
        response = super().form_valid(form)
        diecut_files = self.request.FILES.getlist('diecut_files_multiple')
        for f in diecut_files:
            ProductDocument.objects.create(product=self.object, file=f, doc_type='DIECUT', uploaded_by=self.request.user)
        tech_files = self.request.FILES.getlist('tech_files_multiple')
        for f in tech_files:
            ProductDocument.objects.create(product=self.object, file=f, doc_type='TECH', uploaded_by=self.request.user)
        return response

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:catalog')

class ProductDocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductDocument
    
    def delete(self, request, *args, **kwargs):
        document = self.get_object()
        document.file.delete(save=False) # delete physical file
        document.delete()
        if request.htmx:
            return HttpResponse("")
        return HttpResponse(status=204) # Fallback
