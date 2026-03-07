from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction

from users.models import User
from customers.models import Customer
from .models import QuoteRequest
from .forms import QuoteRequestForm, QuoteProductFormSet


class PortalClientMixin(UserPassesTestMixin):
    """Permite el acceso solo a usuarios con rol PORTAL."""
    def test_func(self):
        return self.request.user.role == User.Roles.PORTAL


class InternalStaffMixin(UserPassesTestMixin):
    """Permite el acceso a staff interno (Admin, Gerencia, Ventas)."""
    def test_func(self):
        allowed_roles = [User.Roles.ADMIN, User.Roles.MANAGEMENT, User.Roles.SALES]
        return self.request.user.role in allowed_roles


class PortalView(LoginRequiredMixin, PortalClientMixin, TemplateView):
    template_name = 'quotes/portal.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mostrar historia de cotizaciones si quisieramos
        return context


class QuoteCreateView(LoginRequiredMixin, PortalClientMixin, CreateView):
    model = QuoteRequest
    form_class = QuoteRequestForm
    template_name = 'quotes/quote_form.html'
    success_url = reverse_lazy('quotes:portal_home')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['products'] = QuoteProductFormSet(self.request.POST)
        else:
            data['products'] = QuoteProductFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        products = context['products']
        
        with transaction.atomic():
            self.object = form.save(commit=False)
            # Default to requester email if not provided (though form usually mandates it)
            self.object.save()
            
            if products.is_valid():
                products.instance = self.object
                products.save()
            else:
                return self.form_invalid(form)
                
        messages.success(self.request, "Solicitud de cotización enviada correctamente.")
        return super().form_valid(form)


class QuoteListView(LoginRequiredMixin, InternalStaffMixin, ListView):
    model = QuoteRequest
    template_name = 'quotes/quote_list.html'
    context_object_name = 'quotes'
    paginate_by = 20
    
    def get_queryset(self):
        # Todos los empleados permitidos ven las cotizaciones pendientes o las contactadas/aprobadas
        return QuoteRequest.objects.all().prefetch_related('products__product')


class QuoteApproveView(LoginRequiredMixin, InternalStaffMixin, View):
    def post(self, request, pk, *args, **kwargs):
        quote = get_object_or_404(QuoteRequest, pk=pk)
        
        if quote.status == 'APPROVED':
            messages.warning(request, "Esta cotización ya fue aprobada.")
            return redirect('quotes:quote_list')
            
        with transaction.atomic():
            # Check if customer exists by CUIT
            customer = Customer.objects.filter(tax_id=quote.requester_cuit).first()
            
            if customer:
                # Link existing customer
                quote.customer = customer
            else:
                # Create new customer
                address_str = f"{quote.billing_address}, {quote.billing_city}" if quote.billing_city else quote.billing_address
                customer = Customer.objects.create(
                    name=quote.requester_name,
                    tax_id=quote.requester_cuit,
                    email=quote.requester_email,
                    phone=quote.requester_phone,
                    address=address_str,
                    assigned_to=request.user 
                )
                quote.customer = customer
            
            # Update quote status
            quote.status = 'APPROVED'
            quote.assigned_to = request.user
            quote.save()
            
        messages.success(request, f"Cotización #{quote.id} aprobada y vinculada al cliente {customer.name}.")
        return redirect('quotes:quote_list')
