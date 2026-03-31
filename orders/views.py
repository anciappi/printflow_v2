from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Case, When, Value, IntegerField
from django.template.loader import render_to_string
from decimal import Decimal

from .models import WorkOrder
from .forms import WorkOrderForm
from inventory.models import InventoryUnit, ConsumptionLog
from products.models import Product


# ---------------------------------------------------------------------------
# PRODUCTION STATUSES — states where material consumption is allowed
# ---------------------------------------------------------------------------
CONSUMABLE_STATUSES = {'PRODUCTION', 'FINISHING', 'QUALITY_CONTROL', 'READY', 'DELIVERED'}


# ---------------------------------------------------------------------------
# SHARED HELPER — builds stock panel context for a given order (DRY)
# ---------------------------------------------------------------------------
def _build_stock_context(order):
    """Returns context dict for the stock_panel fragment."""
    import re
    material = order.product.substrate

    # We fetch them without order_by then sort in Python for natural sorting
    stock_units_qs = InventoryUnit.objects.filter(
        material=material,
        status__in=['AVAILABLE', 'IN_USE']
    ).select_related('purchase_order', 'material')

    stock_total = stock_units_qs.aggregate(total=Sum('current_quantity'))['total'] or Decimal('0')

    # Natural sort function (same as in inventory/views.py)
    def natural_sort_key(unidad):
        parts = [int(text) if text.isdigit() else text.lower() 
                 for text in re.split('([0-9]+)', unidad.unit_number)]
        remito = unidad.purchase_order.remito_number if unidad.purchase_order else 'IMPORT'
        return (remito, parts)

    stock_units = list(stock_units_qs)
    stock_units.sort(key=natural_sort_key)

    consumos_ot = ConsumptionLog.objects.filter(
        reference_ot=order.ot_number
    ).select_related('inventory_unit__material', 'responsible').order_by('-date')

    return {
        'order': order,
        'material': material,
        'stock_units': stock_units,
        'stock_total': stock_total,
        'consumos_ot': consumos_ot,
        'can_consume': order.current_status in CONSUMABLE_STATUSES,
    }


def _render_stock_panel(request, order, extra_ctx=None):
    """Renders the stock_panel fragment with optional extra context (e.g. error)."""
    ctx = _build_stock_context(order)
    if extra_ctx:
        ctx.update(extra_ctx)
    html = render_to_string('orders/fragments/stock_panel.html', ctx, request=request)
    return HttpResponse(html)


# ---------------------------------------------------------------------------
# VIEWS
# ---------------------------------------------------------------------------

class WorkOrderListView(LoginRequiredMixin, ListView):
    model = WorkOrder
    template_name = 'orders/workorder_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        return WorkOrder.objects.select_related(
            'product__customer', 'sales_rep', 'branch'
        ).annotate(
            is_delivered=Case(
                When(current_status='DELIVERED', then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('is_delivered', '-created_at')


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
            'product__customer', 'product__substrate', 'sales_rep', 'branch'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_build_stock_context(self.object))
        return context


class WorkOrderStatusUpdateView(LoginRequiredMixin, View):
    """
    Handles status transitions via HTMX POST.
    Returns updated status badge fragment + fires 'statusUpdated' event so
    the stock panel can re-fetch itself automatically.
    """
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

        html = render_to_string(
            'orders/fragments/status_badge.html',
            {'order': order},
            request=request
        )
        response = HttpResponse(html)
        # Notify stock panel to re-fetch — can_consume may have changed
        response['HX-Trigger'] = 'statusUpdated'
        return response


class WorkOrderStockPanelView(LoginRequiredMixin, View):
    """
    GET endpoint for the stock panel fragment.
    Used by HTMX to re-render the panel after a status transition
    (triggered by HX-Trigger: statusUpdated from WorkOrderStatusUpdateView).
    """
    def get(self, request, pk):
        order = get_object_or_404(
            WorkOrder.objects.select_related('product__substrate'),
            pk=pk
        )
        return _render_stock_panel(request, order)


class WorkOrderProgressView(LoginRequiredMixin, View):
    """
    GET endpoint for the progress bar fragment.
    Used by HTMX to re-render the progress bar after a status transition
    (triggered by HX-Trigger: statusUpdated).
    """
    def get(self, request, pk):
        order = get_object_or_404(WorkOrder, pk=pk)
        html = render_to_string('orders/fragments/progress_bar.html', {'order': order}, request=request)
        return HttpResponse(html)


class LoadCustomerProductsView(LoginRequiredMixin, View):
    """
    HTMX endpoint that returns <option> elements of products filtered by customer
    """
    def get(self, request):
        customer_id = request.GET.get('customer')
        if customer_id:
            # We filter by customer and only show ACTIVE products
            products = Product.objects.filter(customer_id=customer_id, status='ACTIVE').order_by('name')
        else:
            products = Product.objects.none()
            
        html = render_to_string(
            'orders/fragments/product_options.html', 
            {'products': products}, 
            request=request
        )
        return HttpResponse(html)


class WorkOrderConsumoView(LoginRequiredMixin, View):
    """
    Handles manual stock deduction from the OT detail page via HTMX POST.
    Reuses inventory.ConsumptionLog — auto-links reference_ot to the OT number.
    Returns updated stock_panel fragment.
    """
    def post(self, request, pk):
        order = get_object_or_404(
            WorkOrder.objects.select_related('product__substrate'),
            pk=pk
        )

        # Guard: only allowed from PRODUCTION onwards
        if order.current_status not in CONSUMABLE_STATUSES:
            return _render_stock_panel(
                request, order,
                error='El descuento de material solo está disponible a partir de "En Producción".'
            )

        unit_id = request.POST.get('unit_id')
        cantidad_texto = request.POST.get('cantidad')

        if not unit_id or not cantidad_texto:
            return _render_stock_panel(
                request, order,
                error='Seleccioná una unidad e ingresá la cantidad.'
            )

        try:
            unit = get_object_or_404(
                InventoryUnit,
                pk=unit_id,
                material=order.product.substrate,
                status__in=['AVAILABLE', 'IN_USE']
            )
            cantidad = Decimal(cantidad_texto)

            if cantidad <= 0:
                return _render_stock_panel(request, order, error='La cantidad debe ser mayor a cero.')

            if cantidad > unit.current_quantity:
                return _render_stock_panel(
                    request, order,
                    error=f'Stock insuficiente. Disponible en esta unidad: {unit.current_quantity} ml.'
                )

            ConsumptionLog.objects.create(
                inventory_unit=unit,
                quantity_used=cantidad,
                responsible=request.user,
                reference_ot=order.ot_number,
            )

        except Exception as e:
            return _render_stock_panel(request, order, error=str(e))

        return _render_stock_panel(request, order)
