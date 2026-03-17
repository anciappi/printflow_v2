-- PrintFlow RLS Setup
-- Run after migrate_schemas --shared

CREATE INDEX IF NOT EXISTS idx_users_user_tenant_id
    ON users_user(tenant_id);

ALTER TABLE users_user ENABLE ROW LEVEL SECURITY;
ALTER TABLE users_user FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON users_user;
DROP POLICY IF EXISTS superadmin_bypass ON users_user;

-- Superadmin bypass — anciappi can do everything
CREATE POLICY superadmin_bypass ON users_user
    AS PERMISSIVE
    FOR ALL
    TO printflow_user
    USING (
        current_setting('app.current_tenant_id', true) = ''
        OR current_setting('app.current_tenant_id', true) IS NULL
    )
    WITH CHECK (
        current_setting('app.current_tenant_id', true) = ''
        OR current_setting('app.current_tenant_id', true) IS NULL
    );

-- Tenant isolation — regular users see only their tenant
CREATE POLICY tenant_isolation ON users_user
    AS PERMISSIVE
    FOR ALL
    TO printflow_user
    USING (
        tenant_id IS NULL
        OR
        tenant_id::text = coalesce(
            current_setting('app.current_tenant_id', true),
            ''
        )
    )
    WITH CHECK (
        tenant_id IS NULL
        OR
        tenant_id::text = coalesce(
            current_setting('app.current_tenant_id', true),
            ''
        )
    );

-- Verify
SELECT policyname, permissive, roles, cmd
FROM pg_policies
WHERE tablename = 'users_user';