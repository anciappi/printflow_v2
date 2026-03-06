from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import WorkOrder
from .forms import WorkOrderForm

class WorkOrderListView(LoginRequiredMixin, ListView):
    model = WorkOrder
    template_name = 'orders/workorder_list.html'
    context_object_name = 'orders'

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
