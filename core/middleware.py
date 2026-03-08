from django.shortcuts import redirect
from django.urls import reverse
from users.models import User


class PortalMiddleware:
    """
    Middleware to enforce strict routing for PORTAL users vs internal users.

    Rules:
    1. Unauthenticated users are handled by standard @login_required decorators.
       This middleware only acts on authenticated users.

    2. If user.role == PORTAL:
       - They can ONLY access URLs starting with /portal/ or /logout/.
       - Any other URL redirects to /portal/.

    3. If user.role != PORTAL (internal staff):
       - They can access /portal/list/ and /portal/approve/ (management views).
       - They cannot access /portal/ or /portal/new/ (external client views).
       - Any attempt to access those redirects to the internal dashboard.
    """

    # Internal staff can access these portal URLs
    INTERNAL_PORTAL_URLS = ['/portal/list', '/portal/approve']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
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

        # Internal users → can access /portal/list/ and /portal/approve/
        # but NOT /portal/ or /portal/new/ (external client views only)
        else:
            if is_portal_url and not is_internal_portal_url:
                return redirect('inventory:dashboard')

        return self.get_response(request)