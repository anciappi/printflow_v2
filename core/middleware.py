from django.shortcuts import redirect
from django.urls import reverse
from users.models import User


class PortalMiddleware:
    """
    Middleware to enforce strict routing for PORTAL users vs internal users.
    Runs AFTER TenantMainMiddleware — request.tenant is always available.

    Rules:
    1. Public schema (PrintFlow superadmin): bypass all rules.
    2. Unauthenticated users: handled by @login_required decorators.
    3. PORTAL users:
       - Can ONLY access URLs starting with /portal/ or /logout/.
       - Any other URL redirects to /portal/.
    4. Internal staff:
       - Can access management portal URLs (list, approve, card-jobs).
       - Cannot access external client portal URLs (/portal/, /portal/new/).
       - Any attempt redirects to inventory dashboard.

    Building analogy:
       - request.tenant = the floor (PrintShop / Grupo Velton)
       - request.user.role = the key that opens certain rooms
    """

    # Internal staff can access these portal URLs
    INTERNAL_PORTAL_URLS = [
        '/portal/list',
        '/portal/approve',
        '/portal/card-jobs',
        '/portal/card-job/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Bypass: public schema is the PrintFlow superadmin — no portal rules apply
        if hasattr(request, 'tenant') and request.tenant.schema_name == 'public':
            return self.get_response(request)

        user = request.user

        # Tenant scoping — prevent users from accessing wrong tenant
        if user.is_authenticated and hasattr(request, 'tenant'):
            if not user.is_superadmin and user.tenant != request.tenant:
                from django.contrib.auth import logout
                logout(request)
                return redirect('login')

        path = request.path_info

        # Skip unauthenticated users, static and media files
        if not user.is_authenticated or \
           path.startswith('/portal/login/') or \
           path.startswith('/static/') or \
           path.startswith('/media/') or \
           path.startswith('/__debug__/'):
            return self.get_response(request)

        is_portal_url = path.startswith('/portal/')
        is_internal_portal_url = any(
            path.startswith(u) for u in self.INTERNAL_PORTAL_URLS
        )
        is_logout_url = path == reverse('logout')

        # PORTAL users → only /portal/ URLs allowed
        if user.role == User.Roles.PORTAL:
            if not is_portal_url and not is_logout_url:
                return redirect('quotes:portal_home')

        # Internal staff → can access management portal URLs
        # but NOT external client portal views
        else:
            if is_portal_url and not is_internal_portal_url:
                return redirect('inventory:dashboard')

        return self.get_response(request)