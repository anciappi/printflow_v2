"""
RLS and tenant isolation tests for PrintFlow.
These tests verify that PostgreSQL Row Level Security
is working correctly at the database level.
"""
import pytest
from django.db import connection
from django_tenants.utils import schema_context
from users.models import User
from tenants.models import PrintShop, Domain, Branch


@pytest.fixture
def velton_tenant(db):
    tenant = PrintShop.objects.create(
        schema_name='test_velton',
        name='Test Velton',
        plan='pro'
    )
    Domain.objects.create(
        domain='testvelton.localhost',
        tenant=tenant,
        is_primary=True
    )
    return tenant


@pytest.fixture
def magtik_tenant(db):
    tenant = PrintShop.objects.create(
        schema_name='test_magtik',
        name='Test Magtik',
        plan='pro'
    )
    Domain.objects.create(
        domain='testmagtik.localhost',
        tenant=tenant,
        is_primary=True
    )
    return tenant


@pytest.fixture
def superadmin(db):
    return User.objects.create_superuser(
        username='test_superadmin',
        email='super@test.com',
        password='testpass123',
        tenant=None,
    )


@pytest.fixture
def velton_user(db, velton_tenant):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT set_config('app.current_tenant_id', %s, false)",
            [str(velton_tenant.id)]
        )
    return User.objects.create_user(
        username='test_velton_user',
        email='velton@test.com',
        password='testpass123',
        tenant=velton_tenant,
    )


@pytest.fixture
def magtik_user(db, magtik_tenant):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT set_config('app.current_tenant_id', %s, false)",
            [str(magtik_tenant.id)]
        )
    return User.objects.create_user(
        username='test_magtik_user',
        email='magtik@test.com',
        password='testpass123',
        tenant=magtik_tenant,
    )


@pytest.mark.django_db
class TestRLSSuperadmin:

    def test_superadmin_sees_all_users(self, superadmin, velton_user, magtik_user):
        """Superadmin with no tenant context sees all users."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT set_config('app.current_tenant_id', '', false)", []
            )
        usernames = list(User.objects.values_list('username', flat=True))
        assert 'test_superadmin' in usernames
        assert 'test_velton_user' in usernames
        assert 'test_magtik_user' in usernames

    def test_superadmin_has_no_tenant(self, superadmin):
        """Superadmin tenant field must be None."""
        assert superadmin.tenant is None

    def test_superadmin_is_superadmin_property(self, superadmin):
        """is_superadmin property returns True for staff with no tenant."""
        assert superadmin.is_superadmin is True


@pytest.mark.django_db
class TestRLSTenantIsolation:

    def test_velton_context_sees_only_velton_users(
        self, superadmin, velton_user, magtik_user, velton_tenant
    ):
        """Under Velton RLS context, only Velton users are visible."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT set_config('app.current_tenant_id', %s, false)",
                [str(velton_tenant.id)]
            )
        usernames = list(User.objects.values_list('username', flat=True))
        assert 'test_velton_user' in usernames
        assert 'test_superadmin' in usernames  # superadmin always visible
        assert 'test_magtik_user' not in usernames  # cross-tenant blocked

    def test_magtik_context_sees_only_magtik_users(
        self, superadmin, velton_user, magtik_user, magtik_tenant
    ):
        """Under Magtik RLS context, only Magtik users are visible."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT set_config('app.current_tenant_id', %s, false)",
                [str(magtik_tenant.id)]
            )
        usernames = list(User.objects.values_list('username', flat=True))
        assert 'test_magtik_user' in usernames
        assert 'test_superadmin' in usernames
        assert 'test_velton_user' not in usernames

    def test_unknown_tenant_context_sees_only_superadmin(
        self, superadmin, velton_user, magtik_user
    ):
        """Unknown tenant context sees only superadmin users."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT set_config('app.current_tenant_id', '99999', false)", []
            )
        usernames = list(User.objects.values_list('username', flat=True))
        assert 'test_superadmin' in usernames
        assert 'test_velton_user' not in usernames
        assert 'test_magtik_user' not in usernames

    def test_rls_blocks_cross_tenant_insert(
        self, velton_user, magtik_tenant, velton_tenant
    ):
        """RLS must block inserting a user into wrong tenant context."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT set_config('app.current_tenant_id', %s, false)",
                [str(velton_tenant.id)]
            )
        import pytest as pt
        with pt.raises(Exception):
            User.objects.create_user(
                username='intruder',
                email='intruder@test.com',
                password='testpass123',
                tenant=magtik_tenant,  # Wrong tenant!
            )


@pytest.mark.django_db
class TestTenantUserProperty:

    def test_tenant_user_is_not_superadmin(self, velton_user):
        """Regular tenant user is_superadmin must be False."""
        assert velton_user.is_superadmin is False

    def test_tenant_user_has_tenant(self, velton_user, velton_tenant):
        """Tenant user must have tenant assigned."""
        assert velton_user.tenant == velton_tenant
