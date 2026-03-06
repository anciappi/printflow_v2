from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import WorkOrder
from .forms import WorkOrderForm

class WorkOrderListView(LoginRequiredMixin, ListView):
    model = WorkOrder
    template_name = 'orders/workorder_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        return WorkOrder.objects.filter(sales_rep=self.request.user).select_related('customer', 'product')

class WorkOrderCreateView(LoginRequiredMixin, CreateView):
    model = WorkOrder
    form_class = WorkOrderForm
    template_name = 'orders/workorder_form.html'
    success_url = reverse_lazy('orders:list')

class WorkOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = WorkOrder
    form_class = WorkOrderForm
    template_name = 'orders/workorder_form.html'
    success_url = reverse_lazy('orders:list')

    def get_queryset(self):
        return WorkOrder.objects.filter(sales_rep=self.request.user)

class WorkOrderDetailView(LoginRequiredMixin, DetailView):
    model = WorkOrder
    template_name = 'orders/workorder_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return WorkOrder.objects.filter(sales_rep=self.request.user)
