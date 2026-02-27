from django.shortcuts import render, redirect
from .models import Product
from .forms import ProductForm
from customers.models import Customer

def product_catalog(request):
    # Obtenemos clientes que tengan al menos un producto activo
    # Ordenamos por nombre para que la lista sea fácil de navegar
    customers = Customer.objects.filter(products__isnull=False).distinct().prefetch_related('products').order_by('name')
    
    context = {
        'customers': customers
    }
    return render(request, 'products/product_catalog.html', context)


def product_create(request):
    if request.method == 'POST':
        # request.FILES es necesario para procesar imágenes/PDFs
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Redirigimos al catálogo para ver el nuevo producto
            return redirect('products:catalog')
    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {'form': form})