import pytest
from django.db import connection


@pytest.fixture(scope='session')
def apply_rls_policies(django_db_setup, django_db_blocker):
    """
    Applies RLS policies to test database after django_db_setup creates it.
    Depends explicitly on django_db_setup to guarantee correct order.
    """
    with django_db_blocker.unblock():
        with connection.cursor() as cursor:
            cursor.execute(
                "ALTER TABLE users_user ENABLE ROW LEVEL SECURITY;"
            )
            cursor.execute(
                "ALTER TABLE users_user FORCE ROW LEVEL SECURITY;"
            )
            cursor.execute(
                "DROP POLICY IF EXISTS superadmin_bypass ON users_user;"
            )
            cursor.execute(
                "DROP POLICY IF EXISTS tenant_isolation ON users_user;"
            )
            cursor.execute("""
                CREATE POLICY superadmin_bypass ON users_user
                    AS PERMISSIVE FOR ALL TO PUBLIC
                    USING (
                        coalesce(current_setting('app.current_tenant_id', true), '') = ''
                    )
                    WITH CHECK (
                        coalesce(current_setting('app.current_tenant_id', true), '') = ''
                    );
            """)
            cursor.execute("""
                CREATE POLICY tenant_isolation ON users_user
                    AS PERMISSIVE FOR ALL TO PUBLIC
                    USING (
                        tenant_id IS NULL
                        OR tenant_id::text = coalesce(
                            current_setting('app.current_tenant_id', true), ''
                        )
                    )
                    WITH CHECK (
                        tenant_id IS NULL
                        OR tenant_id::text = coalesce(
                            current_setting('app.current_tenant_id', true), ''
                        )
                    );
            """)