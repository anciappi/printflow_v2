from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from customers.models import Customer
from inventory.models import Material
from orders.models import WorkOrder
from purchasing.models import PurchaseOrder
from django.db.models import Sum, Q


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Clientes activos (últimos 5)
        context['recent_customers'] = Customer.objects.filter(
            is_active=True
        ).order_by('-created_at')[:5]
        context['total_customers'] = Customer.objects.filter(is_active=True).count()

        # Materiales con stock activo
        context['materials'] = Material.objects.annotate(
            total_stock=Sum(
                'units__current_quantity',
                filter=Q(units__status__in=['AVAILABLE', 'IN_USE'])
            )
        ).filter(total_stock__gt=0).order_by('name')[:10]
        context['total_materials'] = Material.objects.count()

        # Órdenes de compra pendientes
        context['pending_purchases'] = PurchaseOrder.objects.filter(
            status='PENDING'
        ).select_related('supplier').prefetch_related('items__material')[:5]
        context['total_pending_purchases'] = PurchaseOrder.objects.filter(status='PENDING').count()

        # Órdenes vigentes (excluye DELIVERED y CANCELLED)
        active_statuses = ['PENDING', 'PREPRESS', 'PRODUCTION', 'FINISHING', 'QUALITY_CONTROL', 'READY']
        context['active_orders'] = WorkOrder.objects.filter(
            current_status__in=active_statuses
        ).select_related('product__customer', 'sales_rep').order_by('due_date')
        context['total_active_ots'] = context['active_orders'].count()

        return context