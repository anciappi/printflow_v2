from django.shortcuts import redirect
from django.urls import reverse
from users.models import User


class PortalMiddleware:
    """
    Enforces strict routing between portal clients and internal staff.

    Rules:
    1. Public schema (superadmin): bypass all rules.
    2. Unauthenticated: handled by @login_required decorators.
    3. PORTAL users: can ONLY access /portal/ URLs and /logout/.
       Any other URL redirects to portal home.
    4. STAFF (any role except PORTAL): full access to all URLs.
       No restrictions — granular permissions defined per view.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Bypass: superadmin on public schema
        if hasattr(request, 'tenant') and request.tenant.schema_name == 'public':
            return self.get_response(request)

        user = request.user

        # Tenant scoping — prevent cross-tenant access
        if user.is_authenticated and hasattr(request, 'tenant'):
            if not user.is_superadmin and user.tenant != request.tenant:
                from django.contrib.auth import logout
                logout(request)
                return redirect('login')

        path = request.path_info

        # Skip unauthenticated, static, media, debug
        if not user.is_authenticated or \
           path.startswith('/portal/login/') or \
           path.startswith('/static/') or \
           path.startswith('/media/') or \
           path.startswith('/__debug__/'):
            return self.get_response(request)

        is_portal_url = path.startswith('/portal/')
        is_logout_url = path == reverse('logout')

        # PORTAL users — strictly limited to portal URLs
        if user.role == User.Roles.PORTAL:
            if not is_portal_url and not is_logout_url:
                return redirect('quotes:portal_home')

        # STAFF — no URL restrictions, full access
        # Granular permissions handled per view via StaffMixin

        return self.get_response(request)