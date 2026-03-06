import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction
from django.utils import timezone

# Models now live in this app
from .models import PurchaseOrder, Supplier
from .forms import PurchaseOrderForm, PurchaseOrderItemFormSet, SupplierForm


# ---------------------------------------------------------------------------
# ÓRDENES DE COMPRA
# ---------------------------------------------------------------------------

class PurchaseOrderListView(LoginRequiredMixin, ListView):
    """Lista todas las OC, separando pendientes de recibidas."""
    model = PurchaseOrder
    template_name = 'purchasing/oc_list.html'
    context_object_name = 'ordenes'

    def get_queryset(self):
        return (
            PurchaseOrder.objects
            .select_related('supplier', 'branch')
            .prefetch_related('items__material')
            .order_by('status', '-order_date')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context['pendientes'] = qs.filter(status='PENDING')
        context['recibidas'] = qs.filter(status='RECEIVED').order_by('-delivery_date')[:30]
        return context


@login_required
def create_purchase_order(request):
    """Crear una nueva Orden de Compra con sus ítems."""
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        formset = PurchaseOrderItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    po = form.save(commit=False)
                    fecha = timezone.now().strftime('%y%m%d')
                    random_str = str(uuid.uuid4())[:4].upper()
                    po.remito_number = f"OC-{fecha}-{random_str}"
                    po.save()
                    formset.instance = po
                    formset.save()
                    messages.success(request, f"Orden generada: {po.remito_number}")
                    return redirect('purchasing:oc_list')
            except Exception as e:
                messages.error(request, f"Error al guardar: {e}")
    else:
        form = PurchaseOrderForm()
        formset = PurchaseOrderItemFormSet()

    return render(request, 'purchasing/oc_create.html', {
        'form': form,
        'formset': formset,
        'titulo': 'Nueva Orden de Compra',
        'is_edit': False,
    })


@login_required
def edit_purchase_order(request, pk):
    """Editar una OC en estado PENDING."""
    oc = get_object_or_404(PurchaseOrder, pk=pk)

    if oc.status != 'PENDING':
        messages.error(request, "No se puede editar una orden ya recibida.")
        return redirect('purchasing:oc_list')

    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=oc)
        formset = PurchaseOrderItemFormSet(request.POST, instance=oc)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
                messages.success(request, f"Orden {oc.remito_number} actualizada.")
                return redirect('purchasing:oc_list')
    else:
        form = PurchaseOrderForm(instance=oc)
        formset = PurchaseOrderItemFormSet(instance=oc)

    return render(request, 'purchasing/oc_create.html', {
        'form': form,
        'formset': formset,
        'titulo': f'Editar Orden {oc.remito_number}',
        'is_edit': True,
        'oc': oc,
    })


@login_required
def delete_purchase_order(request, pk):
    """Eliminar una OC pendiente."""
    oc = get_object_or_404(PurchaseOrder, pk=pk)

    if oc.status != 'PENDING':
        messages.error(request, "No se puede eliminar una orden ya recibida.")
        return redirect('purchasing:oc_list')

    if request.method == 'POST':
        numero = oc.remito_number
        oc.delete()
        messages.success(request, f"Orden {numero} eliminada.")

    return redirect('purchasing:oc_list')


@login_required
def recibir_oc(request, pk):
    """Marcar OC como recibida y generar unidades de inventario."""
    oc = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == 'POST':
        nuevo_remito = request.POST.get('nuevo_remito_real', '').strip()
        fecha_ingreso = request.POST.get('fecha_ingreso')

        if nuevo_remito:
            oc.vendor_remito = nuevo_remito

        if oc.mark_as_received():
            if fecha_ingreso:
                oc.delivery_date = fecha_ingreso
                oc.save()
            messages.success(
                request,
                f"Ingreso confirmado. Fecha: {oc.delivery_date}. Remito: {oc.vendor_remito or '—'}"
            )
        else:
            messages.error(request, "Esta orden ya fue procesada previamente.")

    return redirect('purchasing:oc_list')


# ---------------------------------------------------------------------------
# PROVEEDORES
# ---------------------------------------------------------------------------

class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'purchasing/supplier_list.html'
    context_object_name = 'proveedores'
    ordering = ['name']


class SupplierCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'purchasing/supplier_form.html'
    success_url = reverse_lazy('purchasing:supplier_list')
    success_message = "Proveedor '%(name)s' creado con éxito."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nuevo Proveedor'
        ctx['is_edit'] = False
        return ctx


class SupplierUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'purchasing/supplier_form.html'
    success_url = reverse_lazy('purchasing:supplier_list')
    success_message = "Proveedor '%(name)s' actualizado."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar: {self.object.name}'
        ctx['is_edit'] = True
        return ctx
