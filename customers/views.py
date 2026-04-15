from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Customer
from .forms import CustomerForm
from orders.models import WorkOrder
from django.db.models import Q

class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.filter(status='ACTIVE').order_by('name')
        context['active_orders'] = WorkOrder.objects.filter(
            product__customer=self.object
        ).exclude(
            current_status__in=['CANCELLED', 'DELIVERED']
        ).select_related('product', 'sales_rep').order_by('-created_at')
        context['completed_orders'] = WorkOrder.objects.filter(
            product__customer=self.object,
            current_status__in=['DELIVERED', 'CANCELLED']
        ).select_related('product', 'sales_rep').order_by('-created_at')
        context['total_orders_count'] = WorkOrder.objects.filter(product__customer=self.object).count()
        return context

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 20

    def get_template_names(self):
        if self.request.htmx:
            return ['customers/fragments/customer_table.html']
        return ['customers/customer_list.html']

    def get_queryset(self):
        queryset = Customer.objects.filter(is_active=True)
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(tax_id__icontains=q)
            )
        return queryset

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customers:list')

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customers:list')
    
class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customers:list')
