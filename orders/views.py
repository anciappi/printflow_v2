from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import WorkOrder
from .forms import WorkOrderForm


class WorkOrderListView(LoginRequiredMixin, ListView):
    model = WorkOrder
    template_name = 'orders/workorder_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        return WorkOrder.objects.select_related(
            'product__customer', 'sales_rep', 'branch'
        ).order_by('-created_at')


class WorkOrderCreateView(LoginRequiredMixin, CreateView):
    model = WorkOrder
    form_class = WorkOrderForm
    template_name = 'orders/workorder_form.html'
    success_url = reverse_lazy('orders:list')

    def form_valid(self, form):
        form.instance.sales_rep = self.request.user
        return super().form_valid(form)


class WorkOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = WorkOrder
    form_class = WorkOrderForm
    template_name = 'orders/workorder_form.html'
    success_url = reverse_lazy('orders:list')

    def get_queryset(self):
        return WorkOrder.objects.select_related('product__customer', 'branch')


class WorkOrderDetailView(LoginRequiredMixin, DetailView):
    model = WorkOrder
    template_name = 'orders/workorder_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return WorkOrder.objects.select_related(
            'product__customer', 'sales_rep', 'branch'
        )


class WorkOrderStatusUpdateView(LoginRequiredMixin, View):
    """
    Handles status transitions via HTMX POST.
    Returns updated status badge HTML fragment.
    """
    # Valid transitions — defines the production flow
    TRANSITIONS = {
        'PENDING':         'PREPRESS',
        'PREPRESS':        'PRODUCTION',
        'PRODUCTION':      'FINISHING',
        'FINISHING':       'QUALITY_CONTROL',
        'QUALITY_CONTROL': 'READY',
        'READY':           'DELIVERED',
    }

    def post(self, request, pk):
        order = get_object_or_404(WorkOrder, pk=pk)
        next_status = self.TRANSITIONS.get(order.current_status)

        if next_status:
            order.current_status = next_status
            if next_status == 'DELIVERED':
                from django.utils import timezone
                order.finished_at = timezone.now()
            order.save()

        # Return updated status fragment for HTMX swap
        from django.template.loader import render_to_string
        html = render_to_string(
            'orders/fragments/status_badge.html',
            {'order': order},
            request=request
        )
        return HttpResponse(html)
