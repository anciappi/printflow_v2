from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Case, When, Value, IntegerField, Count
from django.template.loader import render_to_string
from decimal import Decimal

from .models import WorkOrder, WorkOrderLog
from .forms import WorkOrderForm, WorkOrderLogForm, WorkOrderAdvanceForm
from inventory.models import InventoryUnit, ConsumptionLog
from products.models import Product
from tenants.models import Branch


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
        qs = WorkOrder.objects.select_related(
            'product__customer', 'sales_rep', 'branch'
        ).annotate(
            is_delivered=Case(
                When(current_status='DELIVERED', then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('is_delivered', '-created_at')

        status_filter = self.request.GET.get('status', '')
        if status_filter and status_filter in dict(WorkOrder.STATUS_CHOICES):
            qs = qs.filter(current_status=status_filter)
            
        q = self.request.GET.get('q', '').strip()
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(ot_number__icontains=q) |
                Q(product__customer__name__icontains=q) |
                Q(product__name__icontains=q)
            )

        branch_filter = self.request.GET.get('branch', '')
        if branch_filter:
            qs = qs.filter(branch_id=branch_filter)

        date_from = self.request.GET.get('date_from', '')
        if date_from:
            qs = qs.filter(created_at__gte=date_from)

        date_to = self.request.GET.get('date_to', '')
        if date_to:
            qs = qs.filter(created_at__lte=date_to + " 23:59:59")

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_filter = self.request.GET.get('status', '')
        context['current_status_filter'] = current_filter
        context['current_q'] = self.request.GET.get('q', '').strip()
        context['current_branch'] = self.request.GET.get('branch', '')
        context['current_date_from'] = self.request.GET.get('date_from', '')
        context['current_date_to'] = self.request.GET.get('date_to', '')
        context['status_choices'] = WorkOrder.STATUS_CHOICES
        context['branches'] = Branch.objects.all()

        # Count across ALL orders (unfiltered) so pill counts are always accurate
        all_counts = WorkOrder.objects.values('current_status').annotate(count=Count('id'))
        counts_dict = {item['current_status']: item['count'] for item in all_counts}
        context['total_count'] = sum(counts_dict.values())

        # Build status_data: only include statuses that have orders, plus the active filter
        context['status_data'] = [
            {
                'value': value,
                'label': label,
                'count': counts_dict.get(value, 0),
                'is_active': current_filter == value,
            }
            for value, label in WorkOrder.STATUS_CHOICES
            if counts_dict.get(value, 0) > 0 or current_filter == value
        ]
        return context


class WorkOrderCreateView(LoginRequiredMixin, CreateView):
    model = WorkOrder
    form_class = WorkOrderForm
    template_name = 'orders/workorder_form.html'
    success_url = reverse_lazy('orders:list')

    def get_initial(self):
        initial = super().get_initial()
        product_id = self.request.GET.get('product')
        if product_id:
            try:
                from products.models import Product
                product = Product.objects.get(pk=product_id)
                initial['product'] = product.id
                initial['customer'] = product.customer_id
            except Exception:
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.request.GET.get('product')
        if product_id and not self.object:
            try:
                from products.models import Product
                context['initial_product'] = Product.objects.get(pk=product_id)
            except Exception:
                pass
        return context

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
        context['log_form'] = WorkOrderLogForm()
        context['logs'] = self.object.logs.select_related('user').all()
        return context


class WorkOrderStatusUpdateModalView(LoginRequiredMixin, View):
    """
    Returns the modal for advancing the status of a work order.
    """
    def get(self, request, pk):
        order = get_object_or_404(WorkOrder, pk=pk)
        next_status = WorkOrderStatusUpdateView.TRANSITIONS.get(order.current_status)
        
        if not next_status:
            return HttpResponse("No valid transition", status=400)
            
        next_status_label = dict(WorkOrder.STATUS_CHOICES).get(next_status)
        
        # Pre-fill modal with existing order quantity or sensible defaults
        initial_data = {
            'quantity_produced': order.quantity,
            'bocas': order.bocas,
        }
        
        form = WorkOrderAdvanceForm(initial=initial_data)
        
        html = render_to_string(
            'orders/fragments/status_update_modal.html',
            {
                'order': order,
                'next_status_label': next_status_label,
                'form': form
            },
            request=request
        )
        return HttpResponse(html)


class WorkOrderStatusUpdateView(LoginRequiredMixin, View):
    """
    Handles status transitions via HTMX POST from the Modal.
    Saves new Log entry, updates WorkOrder, and triggers events.
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
            form = WorkOrderAdvanceForm(request.POST)
            if form.is_valid():
                # Extract clean data
                quantity = form.cleaned_data.get('quantity_produced')
                bocas = form.cleaned_data.get('bocas')
                material_used = form.cleaned_data.get('material_used')
                comment = form.cleaned_data.get('comment')
                
                # Update WorkOrder status

                order.current_status = next_status
                if next_status == 'DELIVERED':
                    from django.utils import timezone
                    order.finished_at = timezone.now()
                order.save()
                
                # Create the Work Order Log for the completed status
                WorkOrderLog.objects.create(
                    work_order=order,
                    user=request.user,
                    status=next_status,
                    quantity_produced=quantity,
                    bocas=bocas,
                    material_used=material_used,
                    comment=comment
                )

                # Return empty to close modal, plus Out-Of-Band swap for status badge
                html_badge = render_to_string(
                    'orders/fragments/status_badge.html',
                    {
                        'order': order, 
                        'swap_oob': True,
                        'last_log_quantity': quantity,
                        'last_log_material': material_used
                    },
                    request=request
                )
                # HTMX will put empty string in #modal-container, and swap #status-block automatically
                response = HttpResponse(html_badge)
                # Notify other components (progress bar, log feed, stock panel) to refresh
                response['HX-Trigger'] = 'statusUpdated'
                return response
            else:
                # Form is invalid, return the modal with errors to #modal-container
                next_status_label = dict(WorkOrder.STATUS_CHOICES).get(next_status)
                html_modal = render_to_string(
                    'orders/fragments/status_update_modal.html',
                    {
                        'order': order,
                        'next_status_label': next_status_label,
                        'form': form
                    },
                    request=request
                )
                return HttpResponse(html_modal)
        
        # If no valid transition, just close the modal
        return HttpResponse("")


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


class LoadProductDetailsView(LoginRequiredMixin, View):
    """
    HTMX endpoint that returns a read-only fragment displaying product details 
    (images and technical specifications).
    """
    def get(self, request):
        product_id = request.GET.get('product')
        product = None
        if product_id:
            try:
                # Utilizamos select_related si hubiese foráneas importantes o prefetch si es útil
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                pass
            
        html = render_to_string(
            'orders/fragments/product_details.html', 
            {'product': product}, 
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

class WorkOrderLogCreateView(LoginRequiredMixin, View):
    """
    Handles HTMX endpoint for the Log Feed.
    GET: Returns the rendered log feed fragment (used by log refresh triggers)
    POST: Handles manual creation of a log (Ficha Médica snippet) with just comments.
    """
    def get(self, request, pk):
        order = get_object_or_404(WorkOrder, pk=pk)
        logs = order.logs.select_related('user').all()
        html = render_to_string(
            'orders/fragments/log_feed.html',
            {'order': order, 'log_form': WorkOrderLogForm(), 'logs': logs},
            request=request
        )
        return HttpResponse(html)

    def post(self, request, pk):
        order = get_object_or_404(WorkOrder, pk=pk)
        form = WorkOrderLogForm(request.POST)

        if form.is_valid():
            log = form.save(commit=False)
            log.work_order = order
            log.user = request.user
            log.status = order.current_status
            log.save()
            form = WorkOrderLogForm() # clear form

        logs = order.logs.select_related('user').all()
        html = render_to_string(
            'orders/fragments/log_feed.html',
            {'order': order, 'log_form': form, 'logs': logs},
            request=request
        )
        return HttpResponse(html)

from django.views.generic import UpdateView, DeleteView
from django.shortcuts import render

class WorkOrderLogUpdateView(LoginRequiredMixin, UpdateView):
    model = WorkOrderLog
    form_class = WorkOrderLogForm
    template_name = 'orders/fragments/log_edit_modal.html'

    def form_valid(self, form):
        self.object = form.save()
        order = self.object.work_order
        context = {
            'order': order,
            'logs': order.logs.select_related('user').all(),
            'log_form': WorkOrderLogForm(),
        }
        return render(self.request, 'orders/fragments/log_feed.html', context)

class WorkOrderLogDeleteView(LoginRequiredMixin, DeleteView):
    model = WorkOrderLog

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponse('')

