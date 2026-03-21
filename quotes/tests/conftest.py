"""
Tenant-aware test configuration for quotes app.
"""
import pytest
from django.db import connection
from django.test import Client
from django_tenants.utils import schema_context, tenant_context
from tenants.models import PrintShop, Domain, Branch


@pytest.fixture(scope='session')
def tenant(django_db_setup, django_db_blocker):
    """Creates a test tenant with schema and RLS policies."""
    with django_db_blocker.unblock():
        with connection.cursor() as cursor:
            cursor.execute("ALTER TABLE users_user ENABLE ROW LEVEL SECURITY;")
            cursor.execute("ALTER TABLE users_user FORCE ROW LEVEL SECURITY;")
            cursor.execute("DROP POLICY IF EXISTS superadmin_bypass ON users_user;")
            cursor.execute("DROP POLICY IF EXISTS tenant_isolation ON users_user;")
            cursor.execute("""
                CREATE POLICY superadmin_bypass ON users_user
                    AS PERMISSIVE FOR ALL TO PUBLIC
                    USING (coalesce(current_setting('app.current_tenant_id', true), '') = '')
                    WITH CHECK (coalesce(current_setting('app.current_tenant_id', true), '') = '');
            """)
            cursor.execute("""
                CREATE POLICY tenant_isolation ON users_user
                    AS PERMISSIVE FOR ALL TO PUBLIC
                    USING (
                        tenant_id IS NULL OR
                        tenant_id::text = coalesce(current_setting('app.current_tenant_id', true), '')
                    )
                    WITH CHECK (
                        tenant_id IS NULL OR
                        tenant_id::text = coalesce(current_setting('app.current_tenant_id', true), '')
                    );
            """)

        test_tenant = PrintShop.objects.create(
            schema_name='test_quotes',
            name='Test PrintShop',
            plan='pro'
        )
        Domain.objects.create(
            domain='testquotes.localhost',
            tenant=test_tenant,
            is_primary=True
        )
        yield test_tenant


@pytest.fixture(scope='session')
def tenant_branch(tenant, django_db_blocker):
    """Creates a branch within the test tenant."""
    with django_db_blocker.unblock():
        with schema_context(tenant.schema_name):
            branch = Branch.objects.create(tenant=tenant, name='Test Branch')
        yield branch


@pytest.fixture(autouse=True)
def set_tenant_context(tenant, db):
    """
    Activates tenant schema and sets RLS context for every test.
    Also patches the default test client to use tenant's domain.
    """
    with tenant_context(tenant):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT set_config('app.current_tenant_id', %s, false)",
                [str(tenant.id)]
            )
        yield

@pytest.fixture
def auth_client(tenant):
    """
    Returns an authenticated client factory for the test tenant.
    Injects the user directly into the session, bypassing the
    login flow to avoid tenant middleware interference.
    """
    from django.test import Client
    from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY
    from django.contrib.sessions.backends.db import SessionStore
    from django_tenants.utils import tenant_context

    def make_client(user, password='testpass123'):
        c = Client(SERVER_NAME='testquotes.localhost')

        with tenant_context(tenant):
            # Create session manually inside tenant schema
            session = SessionStore()
            session[SESSION_KEY] = str(user.pk)
            session[BACKEND_SESSION_KEY] = 'django.contrib.auth.backends.ModelBackend'
            session[HASH_SESSION_KEY] = user.get_session_auth_hash()
            session.save()

        # Set session cookie on client
        c.cookies['sessionid'] = session.session_key
        return c

    return make_client

@pytest.fixture
def client(tenant):
    """
    Returns a Django test client configured for the test tenant's domain.
    Overrides pytest-django's default client fixture.
    """
    from django.test import Client
    c = Client(SERVER_NAME='testquotes.localhost')
    return c