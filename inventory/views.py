import uuid
import re
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import HttpResponse
from django.views.generic import ListView, TemplateView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import Sum, Count, Q, Prefetch
from django.contrib import messages
from decimal import Decimal

#Seguridad
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Importa Modelos y Forms
from .models import InventoryUnit, Material, ConsumptionLog
from purchasing.models import PurchaseOrder, Supplier
from purchasing.forms import PurchaseOrderForm, PurchaseOrderItemFormSet, SupplierForm
from .forms import MaterialForm

# Create your views here.

#Funciones
@login_required
def recibir_oc(request, pk):
    oc = get_object_or_404(PurchaseOrder, pk=pk)
    
    if request.method == 'POST':
        nuevo_remito = request.POST.get('nuevo_remito_real')
        fecha_ingreso = request.POST.get('fecha_ingreso') # <--- Capturamos el nuevo campo
        
        # 1. Guardamos el número de remito físico
        if nuevo_remito and nuevo_remito.strip():
            oc.vendor_remito = nuevo_remito.strip()
            
        # 2. Procesamos el ingreso
        if oc.mark_as_received():
            
            # 3. Si el usuario puso una fecha manual, la actualizamos
            if fecha_ingreso:
                oc.delivery_date = fecha_ingreso
                oc.save()
                
            if request.htmx:
                response = HttpResponse("")
                response['HX-Trigger'] = 'ocUpdated'
                return response

            messages.success(request, f"Ingreso confirmado con fecha {oc.delivery_date}. Remito: {oc.vendor_remito}")
        else:
            if request.htmx:
                return render(request, 'inventory/fragments/recepcion_modal.html', {
                    'oc': oc,
                    'error': 'Este remito ya fue procesado.'
                })
            messages.error(request, "Este remito ya fue procesado.")
            
    return redirect('inventory:oc_list')

@login_required
def delete_purchase_order(request, pk):
    oc = get_object_or_404(PurchaseOrder, pk=pk)
    
    # Seguridad: Solo permitimos borrar si NO fue recibida
    if oc.status != 'PENDING':
        messages.error(request, "No se puede eliminar una orden que ya fue recibida/procesada.")
        return redirect('inventory:oc_list')
        
    if request.method == 'POST':
        numero = oc.remito_number
        oc.delete()
        if request.htmx:
            return HttpResponse("")
        messages.success(request, f"La Orden de Compra {numero} fue eliminada.")
        
    return redirect('inventory:oc_list')

@login_required
def edit_purchase_order(request, pk):
    oc = get_object_or_404(PurchaseOrder, pk=pk)

    # Seguridad: Solo editar pendientes
    if oc.status != 'PENDING':
        messages.error(request, "No se puede editar una orden cerrada.")
        return redirect('inventory:oc_list')

    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=oc, request=request)
        # Importante: instance=oc conecta los items a esta orden
        formset = PurchaseOrderItemFormSet(request.POST, instance=oc)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
                messages.success(request, f"Orden {oc.remito_number} actualizada correctamente.")
                return redirect('inventory:oc_list')
    else:
        form = PurchaseOrderForm(instance=oc, request=request)
        formset = PurchaseOrderItemFormSet(instance=oc)

    # Reutilizamos el template de creación o creamos uno nuevo. 
    # Para no confundir, usaremos uno específico 'oc_edit.html'
    return render(request, 'inventory/oc_edit.html', {
        'form': form,
        'formset': formset,
        'is_edit': True # Bandera para saber que estamos editando
    })

@login_required
def fraccionar_unidad(request, unit_id):
    parent = get_object_or_404(InventoryUnit, pk=unit_id)
    
    if request.method == 'POST':
        try:
            ancho_a = Decimal(request.POST.get('ancho_hija_a'))
            hija_a, hija_b = parent.fraccionar(ancho_a)
            if request.htmx:
                response = HttpResponse("")
                response['HX-Trigger'] = 'inventoryUpdated'
                return response
            messages.success(request, f"Bobina fraccionada en: {hija_a.width_override}cm y {hija_b.width_override}cm")
        except ValueError as e:
            if request.htmx:
                return render(request, 'inventory/fragments/fraccionar_modal.html', {
                    'unit': parent,
                    'error': str(e)
                })
            messages.error(request, str(e))
        except Exception as e:
            if request.htmx:
                return render(request, 'inventory/fragments/fraccionar_modal.html', {
                    'unit': parent,
                    'error': str(e)
                })
            messages.error(request, f"Error inesperado al fraccionar: {e}")
            
    return redirect('inventory:inventory_list')

@login_required
def registrar_consumo(request, unit_id):
    if request.method == 'POST':
        unidad = get_object_or_404(InventoryUnit, id=unit_id)
        cantidad_texto = request.POST.get('cantidad')
        
        # 1. Capturamos los nuevos campos
        fecha_texto = request.POST.get('fecha_consumo')
        ref_ot = request.POST.get('ref_ot')

        try:
            cantidad_decimal = Decimal(cantidad_texto)

            if cantidad_decimal > unidad.current_quantity:
                if request.htmx:
                    return render(request, 'inventory/fragments/consumo_modal.html', {
                        'unit': unidad,
                        'error': f'Error: solo hay {unidad.current_quantity} disponible.'
                    })
                messages.error(request, f"Error: Intentaste consumir {cantidad_decimal} pero solo hay {unidad.current_quantity}.")
                return redirect('inventory:inventory_list')
            
            # 2. Definimos la fecha (Si viene vacía, usa "ahora")
            fecha_final = fecha_texto if fecha_texto else timezone.now()

            # 3. Guardamos con los datos nuevos
            ConsumptionLog.objects.create(
                inventory_unit=unidad,
                quantity_used=cantidad_decimal,
                responsible=request.user,
                date=fecha_final,          # <--- Aquí va la fecha
                reference_ot=ref_ot        # <--- Aquí va la OT
            )
            
            if request.htmx:
                response = HttpResponse("")
                response['HX-Trigger'] = 'inventoryUpdated'
                return response

            messages.success(request, f"Descontado con éxito para OT {ref_ot if ref_ot else 'General'}.")
            
        except Exception as e:
            if request.htmx:
                return render(request, 'inventory/fragments/consumo_modal.html', {
                    'unit': unidad,
                    'error': str(e)
                })
            messages.error(request, f"Error: {e}")
            
    return redirect('inventory:inventory_list')

@login_required
def create_purchase_order(request):
    # 1. Si enviaron el formulario (POST)
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, request=request)
        formset = PurchaseOrderItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    purchase_order = form.save(commit=False)
                    fecha = timezone.now().strftime('%y%m%d')
                    random_str = str(uuid.uuid4())[:4].upper()
                    purchase_order.remito_number = f"OC-{fecha} - {random_str}"
                    purchase_order.save()
                    formset.instance = purchase_order
                    formset.save()
                    messages.success(request, f"Orden generada con ID: {purchase_order.remito_number}")
                    return redirect('inventory:oc_list')
            except Exception as e:
                messages.error(request, f"Error: {e}")
    
    # 2. Si entran por primera vez (GET)
    else:
        form = PurchaseOrderForm(request=request)
        formset = PurchaseOrderItemFormSet()

    # --- IMPORTANTE: ESTE RETURN DEBE ESTAR ALINEADO CON EL 'IF' ---
    # Si lo metes dentro del 'else', fallará en el POST si hay errores.
    return render(request, 'inventory/oc_create.html', {
        'form': form,
        'formset': formset
    })

@login_required
def eliminar_consumo(request, log_id):
    log = get_object_or_404(ConsumptionLog, pk=log_id)
    
    if request.method == 'POST':
        try:
            log.deshacer_consumo()
            if request.htmx:
                return HttpResponse("")
            messages.success(request, "Consumo eliminado. El stock ha sido restaurado.")
        except Exception as e:
            messages.error(request, f"Error al deshacer: {e}")
            
    return redirect('inventory:consumption_history')

@login_required
def deshacer_fraccionamiento(request, unit_id):
    hija = get_object_or_404(InventoryUnit, pk=unit_id)
    padre = hija.parent_unit
    
    if not padre:
        messages.error(request, "Esta unidad no proviene de un corte.")
        return redirect('inventory:inventory_list')
        
    if request.method == 'POST':
        try:
            padre.deshacer_fraccionamiento()
            messages.success(request, f"Corte deshecho. La unidad {padre.unit_number} ha sido restaurada.")
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Error inesperado al unir bobinas: {e}")
            
    return redirect('inventory:inventory_list')

# Clases
# Stock general
class StockDashboardView(LoginRequiredMixin,TemplateView):
    template_name = 'inventory/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Obtenemos la consulta base con los cálculos
        base_qs = Material.objects.annotate(
            total_qty=Sum('units__current_quantity', filter=~Q(units__status='EXHAUSTED')),
            count_units=Count('units', filter=~Q(units__status='EXHAUSTED'))
        )

        # 2. Separamos las aguas
        # A. Materiales con Stock (Mayor a 0)
        context['stock_activo'] = base_qs.filter(total_qty__gt=0).order_by('name')
        
        # B. Materiales Agotados (Igual a 0 o Nulo/Nunca comprados)
        context['stock_agotado'] = base_qs.filter(Q(total_qty=0) | Q(total_qty__isnull=True)).order_by('name')

        context['ordenes_pendientes'] = PurchaseOrder.objects.filter(
            status='PENDING'
        ).select_related('supplier').prefetch_related('items__material').order_by('order_date')

        return context

class InventoryListView(LoginRequiredMixin, ListView):
    model = Material
    template_name = 'inventory/inventory_list.html'
    context_object_name = 'materiales'
    paginate_by = 20

    def get_template_names(self):
        if self.request.htmx:
            return ['inventory/fragments/inventory_table.html']
        return ['inventory/inventory_list.html']

    def get_queryset(self):
        # 2. Limpiamos el QuerySet. 
        # Ya no ordenamos aquí por número, solo filtramos y traemos los datos.
        unidades_qs = InventoryUnit.objects.filter(
            status__in=['AVAILABLE', 'IN_USE']
        ).select_related('purchase_order') # Traemos la OC para ordenar después

        return Material.objects.filter(
            units__status__in=['AVAILABLE', 'IN_USE']
        ).distinct().prefetch_related(
            # 'active_units' será una lista de Python que podemos ordenar manualmente
            Prefetch('units', queryset=unidades_qs, to_attr='active_units')
        ).annotate(
            total_stock=Sum('units__current_quantity', filter=Q(units__status__in=['AVAILABLE', 'IN_USE'])),
            cant_bobinas=Count('units', filter=Q(units__status__in=['AVAILABLE', 'IN_USE']))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 3. Aquí ocurre la magia del "Orden Natural"
        # Esta función rompe el texto "1.a" en ["1", ".a"] y convierte el "1" en número real.
        def natural_sort_key(unidad):
            # Creamos una clave de ordenamiento: (Remito, Numero_de_Unidad)
            
            # Esto separa números de letras: "10.b" -> ['', 10, '.b']
            parts = [int(text) if text.isdigit() else text.lower() 
                     for text in re.split('([0-9]+)', unidad.unit_number)]
            
            # Devolvemos una tupla: Primero agrupa por remito, después ordena por número natural
            remito = unidad.purchase_order.remito_number if unidad.purchase_order else 'IMPORT'
            return (remito, parts)

        # Recorremos cada material y ordenamos su lista interna
        for mat in context['materiales']:
            # .sort() ordena la lista en su lugar usando nuestra llave inteligente
            mat.active_units.sort(key=natural_sort_key)

        return context

class OCListView(LoginRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = 'inventory/purchaseorder_list.html'
    context_object_name = 'ordenes'
    paginate_by = 20

    def get_queryset(self):
        # Mostramos las pendientes de ingreso primero
        return PurchaseOrder.objects.filter(status='PENDING').order_by('-order_date')

class SupplierCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:dashboard')
    success_message = "Proveedor creado con éxito."

class MaterialCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Material
    form_class = MaterialForm
    template_name = 'inventory/material_form.html'
    
    # A dónde ir después de guardar (vuelve a la lista para ver que se creó)
    success_url = reverse_lazy('inventory:inventory_list') 
    
    # El mensaje que pediste
    success_message = "El material '%(name)s' fue cargado con éxito."

class ConsumptionHistoryView(LoginRequiredMixin, ListView):
    model = Material
    template_name = 'inventory/consumption_list.html'
    context_object_name = 'materiales_con_consumo'
    paginate_by = 20

    def get_queryset(self):
        # 1. Traemos materiales que tengan al menos un consumo registrado
        materiales = Material.objects.filter(
            units__consumptions__isnull=False
        ).distinct().prefetch_related(
            'units__consumptions', 
            'units__purchase_order'
        )
        return materiales

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 2. Procesamos los datos para ordenarlos como pide Gerencia (Por OT)
        for mat in context['materiales_con_consumo']:
            # Obtenemos todos los consumos de todas las unidades de este material
            consumos = ConsumptionLog.objects.filter(inventory_unit__material=mat).select_related(
                'inventory_unit', 
                'inventory_unit__purchase_order',
                'responsible'
            ).order_by('reference_ot', '-date') # Ordenar por OT y luego por fecha descendente
            
            # "Pegamos" la lista ordenada al objeto material para usarla en el template
            mat.historial_consumos = consumos
            
            # Calculamos un total histórico solo para mostrar arriba
            mat.total_consumido = sum(c.quantity_used for c in consumos)

        return context
    
# 1. LISTADO MAESTRO
class MaterialListView(LoginRequiredMixin, ListView):
    model = Material
    template_name = 'inventory/material_master_list.html'
    context_object_name = 'materiales'
    ordering = ['name'] # Orden alfabético
    paginate_by = 20

# 2. EDITAR MATERIAL
class MaterialUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Material
    form_class = MaterialForm
    template_name = 'inventory/material_form.html' # Reutilizamos el template de creación!
    success_url = reverse_lazy('inventory:material_list')
    success_message = "El material '%(name)s' fue actualizado correctamente."

# 3. BORRAR MATERIAL
class MaterialDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Material
    template_name = 'inventory/material_confirm_delete.html'
    success_url = reverse_lazy('inventory:material_list')
    success_message = "Material eliminado del sistema."
    
    def form_valid(self, request, *args, **kwargs):
        # Manejo de errores si el material está en uso (ProtectedError)
        try:
            return super().form_valid(request, *args, **kwargs)
        except Exception:
            messages.error(self.request, "No se puede eliminar este material porque tiene stock o movimientos asociados.")
            return redirect('inventory:material_list')

class MaterialDetailView(LoginRequiredMixin, DetailView):
    model = Material
    template_name = 'inventory/inventory_detail.html'
    context_object_name = 'material'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        material = self.get_object()
        
        # Unidades activas
        context['unidades_activas'] = material.units.filter(
            status__in=['AVAILABLE', 'IN_USE']
        ).select_related('purchase_order').order_by('purchase_order__delivery_date', 'unit_number')
        
        # Historial de consumos
        context['consumos'] = ConsumptionLog.objects.filter(
            inventory_unit__material=material
        ).select_related('inventory_unit', 'responsible').order_by('-date')
        
        return context

# -----------------------------------------------------------------------------
# HTMX FRAGMENT VIEWS (Modals)
# -----------------------------------------------------------------------------

class ConsumoModalView(LoginRequiredMixin, View):
    """Returns modal HTML fragment for HTMX consumption request."""
    def get(self, request, unit_id):
        unit = get_object_or_404(InventoryUnit, pk=unit_id)
        return render(request, 'inventory/fragments/consumo_modal.html', {'unit': unit})

class FraccionarModalView(LoginRequiredMixin, View):
    """Returns modal HTML fragment for HTMX fraccionar request."""
    def get(self, request, unit_id):
        unit = get_object_or_404(InventoryUnit, pk=unit_id)
        return render(request, 'inventory/fragments/fraccionar_modal.html', {'unit': unit})

class RecepcionModalView(LoginRequiredMixin, View):
    """Returns modal HTML fragment for HTMX reception request."""
    def get(self, request, pk):
        oc = get_object_or_404(PurchaseOrder, pk=pk)
        return render(request, 'inventory/fragments/recepcion_modal.html', {'oc': oc})

def close_modal(request):
    """Returns empty response to clear modal container."""
    return HttpResponse("")