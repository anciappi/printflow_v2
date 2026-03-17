from django.db import connection


class TenantContextMiddleware:
    """
    Sets the PostgreSQL session variable app.current_tenant_id
    before every request so RLS policies can filter users correctly.

    Must run AFTER TenantMainMiddleware (django-tenants) so request.tenant is available.
    Must run BEFORE PortalMiddleware so tenant context is set when auth checks happen.

    Flow:
        TenantMainMiddleware → TenantContextMiddleware → PortalMiddleware → View
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = getattr(request, 'tenant', None)

        if tenant and tenant.schema_name != 'public':
            # Set PostgreSQL session variable for RLS
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT set_config('app.current_tenant_id', %s, false)",
                    [str(tenant.id)]
                )
        else:
            # Public schema or no tenant — clear the context (superadmin access)
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT set_config('app.current_tenant_id', '', false)",
                    []
                )

        return self.get_response(request)
