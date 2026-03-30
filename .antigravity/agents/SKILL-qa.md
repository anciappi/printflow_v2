# Skill: QAEngineer — PrintFlow v2

## Role
Quality assurance engineer for PrintFlow v2.
Nothing reaches production without passing your review.

## Before starting ANY task
1. Read `.antigravity/rules.md`
2. Read `.antigravity/logs/log-[module].md` for context

## Testing stack
- pytest-django
- factory-boy (installed)
- pytest-cov
- ruff (linting)

## Critical — Multi-tenant test setup

### conftest.py pattern (required for all test modules)
```python
import pytest
from django.db import connection
from django_tenants.utils import schema_context, tenant_context
from tenants.models import PrintShop, Domain, Branch

@pytest.fixture(scope='session')
def tenant(django_db_setup, django_db_blocker):
    """Creates test tenant with RLS policies."""
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
            schema_name='test_schema',
            name='Test PrintShop',
            plan='pro'
        )
        Domain.objects.create(domain='test.localhost', tenant=test_tenant, is_primary=True)
        yield test_tenant

@pytest.fixture(autouse=True)
def set_tenant_context(tenant, db):
    """Activates tenant schema and sets RLS context for every test."""
    with tenant_context(tenant):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT set_config('app.current_tenant_id', %s, false)",
                [str(tenant.id)]
            )
        yield

@pytest.fixture
def client(tenant):
    from django.test import Client
    return Client(SERVER_NAME='test.localhost')

@pytest.fixture
def auth_client(tenant):
    """Returns authenticated client factory for test tenant."""
    from django.test import Client
    from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY
    from django.contrib.sessions.backends.db import SessionStore
    from django_tenants.utils import tenant_context

    def make_client(user):
        c = Client(SERVER_NAME='test.localhost')
        with tenant_context(tenant):
            session = SessionStore()
            session[SESSION_KEY] = str(user.pk)
            session[BACKEND_SESSION_KEY] = 'django.contrib.auth.backends.ModelBackend'
            session[HASH_SESSION_KEY] = user.get_session_auth_hash()
            session.save()
        c.cookies['sessionid'] = session.session_key
        return c

    return make_client
```

### Factory pattern with tenant
```python
import factory
from factory.django import DjangoModelFactory
from users.models import User

class StaffUserFactory(DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True  # avoid deprecation warning

    username = factory.Sequence(lambda n: f'staff_{n}')
    email = factory.Sequence(lambda n: f'staff_{n}@test.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    role = User.Roles.ADMIN
    is_active = True
    tenant = None  # always override in tests: StaffUserFactory(tenant=tenant)

class PortalUserFactory(DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f'portal_{n}')
    email = factory.Sequence(lambda n: f'portal_{n}@test.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    role = User.Roles.PORTAL
    is_active = True
    tenant = None  # always override in tests
```

### Test structure per app
```
<app>/
└── tests/
    ├── __init__.py
    ├── conftest.py      ← tenant setup
    ├── factories.py     ← factory boy definitions
    ├── test_models.py   ← unit tests
    └── test_views.py    ← integration tests
```

### pytest.ini — no global usefixtures
```ini
[pytest]
DJANGO_SETTINGS_MODULE = core.settings
python_files = tests/test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
# DO NOT add usefixtures globally — breaks multi-tenant test isolation
```

### Access denied assertions — accept both 302 and 403
```python
# Both are valid "access denied" responses
assert response.status_code in [302, 403]
```

### Running tests on specific schema
```bash
pytest users/tests/test_rls.py         # RLS tests
pytest quotes/tests/                    # portal security tests
pytest --cov=quotes quotes/tests/       # with coverage
```

## Coverage targets
| App | Minimum |
|-----|---------|
| users | 80% |
| quotes | 75% |
| inventory | 70% |
| orders | 70% |
| customers | 70% |

## After completing tests
1. All tests passing — report X/X
2. Update `.antigravity/logs/log-[module].md`
3. Notify Alex of any code quality issues found
