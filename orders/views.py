from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Order, Product
from .forms import OrderForm, OrderItemFormSet, ProductForm, ProductionLogForm, ProductMaterialFormSet

# --- PRODUCTOS (FICHAS TÉCNICAS) ---
class ProductListView(ListView):
    model = Product
    template_name = 'orders/product_list.html'
    context_object_name = 'products'

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save()
            messages.success(request, f"Producto '{p.name}' creado.")
            return redirect('orders:product_list')
    else:
        form = ProductForm()
    return render(request, 'orders/product_form.html', {'form': form})

# --- ÓRDENES ---
class OrderListView(ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    ordering = ['-created_at']

    def get_queryset(self):
        return Order.objects.select_related('product', 'product__customer', 'branch').order_by('-created_at')

def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    count = Order.objects.count() + 1
                    order.ot_number = f"OT-{timezone.now().year}-{count:04d}"
                    order.created_by = request.user
                    order.save()
                    formset.instance = order
                    formset.save()
                    messages.success(request, f"Orden {order.ot_number} creada.")
                    return redirect('orders:order_detail', pk=order.pk)
            except Exception as e:
                messages.error(request, f"Error: {e}")
    else:
        form = OrderForm()
        formset = OrderItemFormSet()
    return render(request, 'orders/order_form.html', {'form': form, 'formset': formset})

def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    logs = order.logs.all().order_by('-created_at')
    log_form = ProductionLogForm()
    return render(request, 'orders/order_detail.html', {
        'order': order, 'logs': logs, 'log_form': log_form
    })

def add_production_log(request, pk):
    # Lógica de avance (mismo que antes)
    return redirect('orders:order_detail', pk=pk)

def approve_order(request, pk):
    # Lógica de aprobación (mismo que antes)
    return redirect('orders:order_detail', pk=pk)

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = ProductMaterialFormSet(request.POST) # <--- Recibimos materiales
        
        if form.is_valid() and formset.is_valid():
            product = form.save()
            
            formset.instance = product # Vinculamos
            formset.save()
            
            messages.success(request, f"Ficha técnica '{product.name}' creada con su receta.")
            # Redirigimos a la "Ficha Médica" que vamos a crear ahora
            return redirect('orders:product_detail', pk=product.pk) 
    else:
        form = ProductForm()
        formset = ProductMaterialFormSet()
    
    return render(request, 'orders/product_form.html', {
        'form': form, 
        'formset': formset # Pasamos el formset al template
    })

class ProductDetailView(DetailView):
    model = Product
    template_name = 'orders/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Historial de Órdenes (Trazabilidad)
        context['historial_ordenes'] = self.object.order_set.all().order_by('-created_at')
        
        # 2. Estadísticas Básicas
        total_producido = sum(o.total_quantity for o in context['historial_ordenes'])
        context['total_historico'] = total_producido
        
        # 3. Receta (Materiales Estándar)
        context['receta'] = self.object.standard_materials.select_related('material').all()
        
        return context