from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import TemplateView, CreateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db import transaction
from django.db.models import Q

from tenants.models import Branch
from users.models import User
from customers.models import Customer
from .models import QuoteRequest, CardJobOrder
from .forms import (
    QuoteRequestForm, QuoteProductFormSet,
    CardJobOrderClientForm, CardJobOrderStaffForm
)


class PortalClientMixin(UserPassesTestMixin):
    """Allows access to PORTAL role users only."""
    raise_exception = False
    def test_func(self):
        return self.request.user.role == User.Roles.PORTAL

class StaffMixin(UserPassesTestMixin):
    """Allows access to any internal staff — any role except PORTAL."""
    raise_exception = False
    def test_func(self):
        return (self.request.user.is_authenticated and
                self.request.user.role != User.Roles.PORTAL)

class PortalOrStaffMixin(UserPassesTestMixin):
    """Allows access to any authenticated user."""
    raise_exception = False
    def test_func(self):
        return self.request.user.is_authenticated


class PortalView(LoginRequiredMixin, PortalClientMixin, TemplateView):
    template_name = 'quotes/portal.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card_jobs'] = CardJobOrder.objects.filter(
            portal_user=self.request.user
        ).order_by('-created_at')
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


class QuoteListView(LoginRequiredMixin, StaffMixin, ListView):
    model = QuoteRequest
    template_name = 'quotes/quote_list.html'
    context_object_name = 'quotes'
    paginate_by = 20
    raise_exception = False
    login_url = reverse_lazy('inventory:dashboard')
    
    def get_queryset(self):
        # Todos los empleados permitidos ven las cotizaciones pendientes o las contactadas/aprobadas
        return QuoteRequest.objects.all().prefetch_related('products__product')


class QuoteApproveView(LoginRequiredMixin, StaffMixin, View):
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


class PortalLoginView(LoginView):
    template_name = 'quotes/portal_login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.role == User.Roles.PORTAL:
            return reverse_lazy('quotes:portal_home')
        return reverse_lazy('inventory:dashboard')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)


class CardJobOrderCreateView(LoginRequiredMixin, PortalClientMixin, CreateView):
    model = CardJobOrder
    form_class = CardJobOrderClientForm
    template_name = 'quotes/card_job_form.html'
    success_url = reverse_lazy('quotes:portal_home')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.status = 'SUBMITTED'
        if self.request.user.role == User.Roles.PORTAL:
            self.object.portal_user = self.request.user
        self.object.save()
        messages.success(self.request, "Solicitud enviada para revisión.")
        return super().form_valid(form)

    def form_invalid(self, form):
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"CardJobOrder form errors: {form.errors}")
        messages.error(self.request, f"Error en el formulario: {form.errors}")
        return super().form_invalid(form)


class CardJobOrderDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        job = get_object_or_404(CardJobOrder, pk=pk)
        
        # Security check for PORTAL users
        if request.user.role == User.Roles.PORTAL:
            if job.portal_user != request.user:
                return redirect('quotes:portal_home')

        staff_form = None
        if request.user.role in [User.Roles.ADMIN, User.Roles.MANAGEMENT, User.Roles.SALES]:
            staff_form = CardJobOrderStaffForm(instance=job)

        return render(request, 'quotes/card_job_detail.html', {
            'job': job,
            'staff_form': staff_form
        })

    def post(self, request, pk):
        job = get_object_or_404(CardJobOrder, pk=pk)
        
        # Only internal staff can POST (edit technical specs)
        if request.user.role not in [User.Roles.ADMIN, User.Roles.MANAGEMENT, User.Roles.SALES]:
            return redirect('quotes:portal_home')
            
        form = CardJobOrderStaffForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Especificaciones técnicas actualizadas correctamente.")
            return redirect('quotes:card_job_detail', pk=pk)
        
        return render(request, 'quotes/card_job_detail.html', {
            'job': job,
            'staff_form': form
        })


class CardJobOrderListView(LoginRequiredMixin, StaffMixin, ListView):
    model = CardJobOrder
    template_name = 'quotes/card_job_list.html'
    context_object_name = 'jobs'
    paginate_by = 20

    def get_template_names(self):
        if self.request.htmx:
            return ['quotes/fragments/job_table.html']
        return [self.template_name]

    def get_queryset(self):
        qs = CardJobOrder.objects.select_related(
            'assigned_to', 'branch'
        ).order_by('-created_at')

        # Search
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(requester_name__icontains=q) |
                Q(order_number__icontains=q) |
                Q(job_description__icontains=q)
            )

        # Filter by status
        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)

        # Filter by branch
        branch = self.request.GET.get('branch', '').strip()
        if branch:
            qs = qs.filter(branch_id=branch)

        # Filter by date
        date_from = self.request.GET.get('date_from', '').strip()
        date_to = self.request.GET.get('date_to', '').strip()
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = CardJobOrder.STATUS_CHOICES
        context['branches'] = Branch.objects.all()
        context['current_filters'] = {
            'q': self.request.GET.get('q', ''),
            'status': self.request.GET.get('status', ''),
            'branch': self.request.GET.get('branch', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
        }
        return context


class CardJobSubmitView(LoginRequiredMixin, PortalOrStaffMixin, View):
    """
    Transitions CardJobOrder from DRAFT to SUBMITTED.
    Accessible by PORTAL users (their own orders) and internal staff.
    """
    def post(self, request, pk):
        job = get_object_or_404(CardJobOrder, pk=pk)

        # Portal users can only submit their own orders
        if request.user.role == User.Roles.PORTAL:
            if job.requester_email != request.user.email:
                messages.error(request, "No tenés permiso para realizar esta acción.")
                return redirect('quotes:portal_home')

        if job.status != 'DRAFT':
            messages.warning(request, "Esta orden ya fue enviada.")
            if getattr(request, 'htmx', False):
                response = HttpResponse("")
                response['HX-Trigger'] = 'jobUpdated'
                return response
            return redirect('quotes:card_job_detail', pk=pk)

        job.status = 'SUBMITTED'
        job.save()
        messages.success(request, "Orden enviada para revisión del equipo.")

        if getattr(request, 'htmx', False):
            response = HttpResponse("")
            response['HX-Trigger'] = 'jobUpdated'
            return response
        return redirect('quotes:card_job_detail', pk=pk)


class CardJobStaffReviewView(LoginRequiredMixin, StaffMixin, View):
    """
    Transitions CardJobOrder from SUBMITTED to STAFF_REVIEW.
    Staff confirms they are reviewing the order.
    """
    def post(self, request, pk):
        job = get_object_or_404(CardJobOrder, pk=pk)

        if job.status != 'SUBMITTED':
            messages.warning(request, "Esta orden no está en estado Enviado.")
            if getattr(request, 'htmx', False):
                response = HttpResponse("")
                response['HX-Trigger'] = 'jobUpdated'
                return response
            return redirect('quotes:card_job_detail', pk=pk)

        job.status = 'STAFF_REVIEW'
        job.assigned_to = request.user
        job.save()
        messages.success(request, "Orden tomada para revisión.")

        if getattr(request, 'htmx', False):
            response = HttpResponse("")
            response['HX-Trigger'] = 'jobUpdated'
            return response
        return redirect('quotes:card_job_detail', pk=pk)


class CardJobSendToClientView(LoginRequiredMixin, StaffMixin, View):
    """
    Transitions CardJobOrder from STAFF_REVIEW to PENDING_CLIENT.
    Sends approval request to client via UUID token URL.
    """
    def post(self, request, pk):
        job = get_object_or_404(CardJobOrder, pk=pk)

        if job.status != 'STAFF_REVIEW':
            messages.warning(request, "La orden debe estar en revisión antes de enviar al cliente.")
            if getattr(request, 'htmx', False):
                response = HttpResponse("")
                response['HX-Trigger'] = 'jobUpdated'
                return response
            return redirect('quotes:card_job_detail', pk=pk)

        job.status = 'PENDING_CLIENT'
        job.save()
        messages.success(request, f"Orden enviada al cliente. Token: {job.approval_token}")

        if getattr(request, 'htmx', False):
            response = HttpResponse("")
            response['HX-Trigger'] = 'jobUpdated'
            return response
        return redirect('quotes:card_job_detail', pk=pk)


class CardJobClientApprovalView(View):
    """
    Public view — no login required.
    Client approves or rejects via UUID token URL.
    Also accessible by staff to assist clients.
    """
    def get(self, request, token):
        job = get_object_or_404(CardJobOrder, approval_token=token)
        return render(request, 'quotes/card_job_approval.html', {'job': job})

    def post(self, request, token):
        job = get_object_or_404(CardJobOrder, approval_token=token)

        if job.status not in ['PENDING_CLIENT', 'STAFF_REVIEW']:
            messages.error(request, "Esta orden ya fue procesada.")
            return render(request, 'quotes/card_job_approval.html', {
                'job': job,
                'error': 'Esta orden ya fue procesada.'
            })

        decision = request.POST.get('decision')
        approved_by = request.POST.get('approved_by', '').strip()

        VALID_DECISIONS = ['APPROVED', 'APPROVED_WITH_CHANGES', 'REJECTED']
        if decision not in VALID_DECISIONS:
            return render(request, 'quotes/card_job_approval.html', {
                'job': job,
                'error': 'Decisión inválida.'
            })

        job.status = decision
        job.review_result = decision
        job.approved_by = approved_by
        job.approval_date = timezone.now().date()
        job.save()

        return render(request, 'quotes/card_job_approval_success.html', {'job': job})


class CardJobToProductionView(LoginRequiredMixin, StaffMixin, View):
    """
    Transitions CardJobOrder from APPROVED/APPROVED_WITH_CHANGES to IN_PRODUCTION.
    """
    def post(self, request, pk):
        job = get_object_or_404(CardJobOrder, pk=pk)

        if job.status not in ['APPROVED', 'APPROVED_WITH_CHANGES']:
            messages.warning(request, "La orden debe estar aprobada para pasar a producción.")
            if getattr(request, 'htmx', False):
                response = HttpResponse("")
                response['HX-Trigger'] = 'jobUpdated'
                return response
            return redirect('quotes:card_job_detail', pk=pk)

        job.status = 'IN_PRODUCTION'
        job.save()
        messages.success(request, "Orden enviada a producción.")

        if getattr(request, 'htmx', False):
            response = HttpResponse("")
            response['HX-Trigger'] = 'jobUpdated'
            return response
        return redirect('quotes:card_job_detail', pk=pk)


class PortalCreateUserView(LoginRequiredMixin, StaffMixin, View):
    """
    Staff creates a portal user for a client.
    Only requires email and full name.
    Password is auto-generated and shown once to staff.
    """
    template_name = 'quotes/portal_create_user.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        import secrets
        import string

        email = request.POST.get('email', '').strip().lower()
        full_name = request.POST.get('full_name', '').strip()

        if not email or not full_name:
            return render(request, self.template_name, {
                'error': 'Email y nombre completo son requeridos.'
            })

        if User.objects.filter(email=email).exists():
            return render(request, self.template_name, {
                'error': f'Ya existe un usuario con el email {email}.'
            })

        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(12))

        names = full_name.split(' ', 1)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=names[0],
            last_name=names[1] if len(names) > 1 else '',
            role=User.Roles.PORTAL,
            tenant=request.tenant,
        )

        return render(request, self.template_name, {
            'success': True,
            'created_user': user,
            'password': password,
        })
