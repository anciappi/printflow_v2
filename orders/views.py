from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
import uuid # Para generar el número de OT si hiciera falta lógica extra
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order, Product
from .forms import OrderForm, OrderItemFormSet, ProductionLogForm, ProductForm


# 1. LISTADO DE ÓRDENES (DASHBOARD)
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    ordering = ['-created_at']

    def get_queryset(self):
        return Order.objects.select_related('customer', 'branch').order_by('-created_at')

# LISTADO DE PRODUCTOS (CATÁLOGO)
class ProductListView(LoginRequiredMixin,ListView):
    model = Product
    template_name = 'orders/product_list.html'
    context_object_name = 'products'

# 2. CREAR NUEVA OT (Cabecera + Materiales)
@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    
                    # Asignamos la sucursal automáticamente (o pídela en el form si prefieres)
                    # Por ahora la sacamos del usuario o la dejamos fija
                    # order.branch = ... (Si la quitaste del form, asignala aquí)
                    
                    # Generar OT Number
                    count = Order.objects.count() + 1
                    order.ot_number = f"OT-{timezone.now().year}-{count:04d}"
                    order.created_by = request.user
                    order.save()
                    
                    # Guardar materiales
                    formset.instance = order
                    formset.save()

                    # YA NO CREAMOS CardSpecification AQUÍ.
                    # El producto ya tiene toda la info técnica.
                    
                    messages.success(request, f"Orden {order.ot_number} creada para {order.product.name}.")
                    return redirect('orders:order_detail', pk=order.pk)
            except Exception as e:
                messages.error(request, f"Error al crear: {e}")
        else:
            messages.error(request, "Por favor corrige los errores.")
    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    return render(request, 'orders/order_form.html', {
        'form': form,
        'formset': formset
    })

# 3. DETALLE DE LA OT (La vista principal de trabajo)
@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    # Formularios para acciones rápidas en la misma página
    log_form = ProductionLogForm()
    
    # Calcular progreso
    logs = order.logs.all().order_by('-created_at')
    
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'logs': logs,
        'log_form': log_form,
        'card_spec': getattr(order, 'card_spec', None),
        'ticket_spec': getattr(order, 'ticket_spec', None)
    })

# 4. REGISTRAR AVANCE (LOG DE PRODUCCIÓN)
@login_required
def add_production_log(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = ProductionLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.order = order
            log.operator = request.user
            log.save()
            
            # Actualizar estado de la OT si es el primer movimiento
            if order.status == Order.Status.READY:
                order.status = Order.Status.PROGRESS
                order.save()
                
            messages.success(request, "Avance registrado correctamente.")
        else:
            messages.error(request, "Error en los datos de producción.")
            
    return redirect('orders:order_detail', pk=pk)

# 5. APROBAR OT (DISPARADOR DE STOCK)
@login_required
def approve_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        try:
            # Aquí se llamará a la lógica de descuento de stock
            # NOTA: Esto fallará hasta que adaptemos el método approve_for_production en models.py
            # order.approve_for_production() 
            
            # Por ahora simulamos el cambio de estado manual
            order.status = Order.Status.READY
            order.save()
            
            messages.success(request, f"OT-{order.ot_number} aprobada para producción.")
        except Exception as e:
            messages.error(request, f"No se pudo aprobar: {e}")
            
    return redirect('orders:order_detail', pk=pk)

# CREAR PRODUCTO (FICHA TÉCNICA)
@login_required
def create_product(request):
    if request.method == 'POST':
        # request.FILES es necesario para las imágenes
        form = ProductForm(request.POST, request.FILES) 
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Ficha técnica '{product.name}' creada.")
            return redirect('orders:product_list')
    else:
        form = ProductForm()
    
        return render(request, 'orders/product_list.html', {'form': form})