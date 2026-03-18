
## Session: 2026-03-07
**Tasks Completed:**
- **Consistencia Visual:** Rediseño completo de `portal_login.html`, `portal.html` y `quote_form.html` siguiendo estrictamente el `STYLE_GUIDE.md`. Se aplicó una estética corporativa "High-Tech" con fondos oscuros, bordes definidos y tipografía técnica.
- **Skill Update:** Added mandatory `STYLE_GUIDE.md` requirement to the `frontend-crafter` skill to ensure visual consistency.
- **New Model:** Implemented `CardJobOrder` in `quotes/models.py` to handle specialized plastic card printing job orders, including client-facing and technical staff sections. Applied database migrations.
- **CardJobOrder UI:** Built complete hybrid workflow for card job orders. Includes `CardJobOrderClientForm` (for portal) and `CardJobOrderStaffForm` (for internal). Created high-fidelity templates (`card_job_form.html`, `card_job_detail.html`, `card_job_list.html`) strictly following `STYLE_GUIDE.md`. Updated `portal.html` with a second action card for card jobs. Added `form_invalid` debugging to `CardJobOrderCreateView`.
- **Middleware:** Updated `PortalMiddleware` to allow unauthenticated access to `/portal/login/`.
- **System Documentation:** Created `.antigravity/STYLE_GUIDE.md` based on `inventory_list.html` as a reference for future UI consistency.

**Files Created/Modified:**
- `quotes/`: `models.py`, `views.py`, `urls.py`, `forms.py`
- `core/`: `middleware.py`
- `templates/quotes/`: `portal_login.html`, `portal.html`, `card_job_form.html`, `card_job_detail.html`, `card_job_list.html`
- `.antigravity/`: `SESSION_LOG.md`, `STYLE_GUIDE.md`

## Session: 2026-03-08
**Tasks Completed:**
- **Card Job Detail Rebuild:** Rebuilt `card_job_detail.html` following a high-fidelity mockup. Integrated Django template variables, implemented role-based read-only/editable states, and applied visual standards from `STYLE_GUIDE.md` (Backgrounds: `#0f1115`/`#1a1d23`, Borders: `#2d333b`, inline SVGs).
- **Style Guide Adherence:** Ensured absolute compliance with the "High-Tech" aesthetic, removing all Material Symbols and custom CSS in favor of Tailwind utility classes.

**Files Created/Modified:**
- `templates/quotes/card_job_detail.html`: Redesigned from scratch based on mockup.

**Status:** Paused pending Stitch mockup validation with client.

**Next Pending Tasks:**
- Integrate approved Stitch mockup into PrintFlow
- Add approval_token UUID to CardJobOrder model
- Build standalone card_job_approval.html (no base.html)
- Build unified card_job_form.html for staff
- Public approval URL: /aprobar/<uuid>/

**Blockers/Open Questions:**
- None.

## Session: 2026-03-16

**Tasks Completed:**
- **Multi-tenant Foundation (Phase 1):** Installed `django-tenants==3.7.0`. Created `tenants` app with `PrintShop` (TenantMixin) and `Domain` (DomainMixin) models. Reconfigured `settings.py` with `SHARED_APPS`, `TENANT_APPS`, `django_tenants.postgresql_backend` engine, `TenantMainMiddleware` as first middleware, and `PUBLIC_SCHEMA_URLCONF`. Created `core/urls_public.py` for public schema routing. Normalized tenant URLs to English (`/inventory/`, `/customers/`, `/purchasing/`).
- **Database Reset & Initialization:** Reset PostgreSQL DB. Ran `migrate_schemas --shared` to create public schema tables. Bootstrapped mandatory public tenant mapped to `localhost`.
- **First Real Tenant (Phase 2):** Created `Grupo Velton` tenant with `schema_name='velton'` mapped to `velton.localhost`. Verified 17 isolated business tables in `velton` schema.
- **Branch Promoted to Central Concept:** Moved `Branch` model from `inventory` to `tenants`. Added FK to `Branch` in `WorkOrder` (required), `QuoteRequest` (required), `CardJobOrder` (nullable — assigned by staff after client submits portal form). Updated `purchasing` and `inventory` references accordingly. Applied all migrations to both `public` and `velton` schemas.
- **PortalMiddleware Updated:** Rewrote `PortalMiddleware` to be multi-tenant aware. Added `request.tenant.schema_name == 'public'` bypass for superadmin. Maintained existing PORTAL vs internal staff routing logic.
- **Local Development Configured:** Added `velton.localhost` to `/etc/hosts`. Fixed logout redirect error in public schema by adding `login` and `logout` routes to `core/urls_public.py`.
- **Scripts Updated:** Updated `reset_app.sh` to use `migrate_schemas` instead of `migrate`, auto-create public tenant, superadmin, Grupo Velton tenant with Velton and Magtik branches, and velton_admin test user. Updated `runserver.sh` to bind to `0.0.0.0:8001`.
- **Full Smoke Test Passed:** Verified end-to-end flow — superadmin on `localhost`, velton_admin login on `velton.localhost`, dashboard access, schema isolation confirmed.

**Architecture Decisions Logged:**
- Building analogy: PrintFlow (building) → PrintShop/tenant (floor) → Branch (department) → Apps (rooms) → Users (tenants)
- Shared data within tenant: customers, materials, products, suppliers
- Branch-scoped data: work orders, quotes, card job orders
- CardJobOrder.branch is nullable: client submits externally, branch assigned on staff approval
- Superadmin lives in public schema, operational users live in tenant schema
- approved_by in CardJobOrder stays as CharField — external client signature, not a system user

**Files Created/Modified:**
- `tenants/`: `models.py`, `admin.py`
- `core/`: `settings.py`, `urls.py`, `urls_public.py`, `middleware.py`
- `inventory/models.py`: removed local Branch, added import from tenants
- `orders/models.py`: added Branch FK
- `quotes/models.py`: added Branch FK to QuoteRequest and CardJobOrder
- `purchasing/models.py`: updated Branch reference
- `requirements.txt`: added django-tenants==3.7.0
- `reset_app.sh`: full rewrite for multi-tenant
- `runserver.sh`: updated to bind 0.0.0.0:8001

**Pending Tasks — Next Session:**
- Phase 5: SaaS Super Admin Dashboard (create tenants, branches, users from UI)
- Onboarding flow for new tenants
- Create Magtik tenant when needed
- UI/Frontend details noted separately
- Module enable/disable per tenant

**Blockers/Open Questions:**
- None.

**Stock Import — Magtik:**
- Created `inventory/management/commands/import_stock.py` — management command to import stock history from Excel files
- Made `InventoryUnit.purchase_order` nullable to support historical imports without purchase orders
- Fixed `natural_sort_key` in `inventory/views.py` to handle None purchase_order
- Fixed `InventoryUnit.__str__` to handle None purchase_order (shows 'IMPORT')
- Successfully imported 10 years of Magtik stock history: 31 materials, 4.846 units, 63 skipped
- Installed `openpyxl` dependency

**Usage:**
```bash
# Dry run first
python manage.py import_stock --file=imports/FILE.xlsx --branch=BRANCH --schema=SCHEMA --dry-run
# Real import
python manage.py import_stock --file=imports/FILE.xlsx --branch=BRANCH --schema=SCHEMA
```

**Pending:**
- Import Velton stock file when available
- UI import form (Phase post-MVP)
- Fix source data issues in Magtik Excel (less than 48hs of configuration)

**Security Issue Identified & Pending Resolution:**
- Detected critical security flaw: users in `public` schema are visible across all tenants
- Attempted solutions: users in TENANT_APPS, Option C (tenant FK), signals — all failed or deemed insufficient
- Root cause: `django-tenants` limitation — Django Admin requires auth tables in `public`
- Decision: Implement PostgreSQL Row Level Security (RLS) for true DB-level user isolation
- Current state: Reverted to original working configuration (users in SHARED_APPS)
- RLS implementation planned for next session — requires fresh architectural design

**Known Security Risk (temporary):**
- User isolation is currently enforced by code (middleware + view scoping) not by DB
- Acceptable for development phase with single client (Grupo Velton)
- Must be resolved before onboarding second real client

## Session: 2026-03-17

**Tasks Completed:**
- **RLS Implementation:** Implemented PostgreSQL Row Level Security for user isolation.
  - Added `tenant` FK to `User` model (`null=True` = superadmin)
  - Created `scripts/rls_setup.sql` with RLS policy, index, and FORCE RLS
  - Created `core/tenant_context.py` — `TenantContextMiddleware` sets `app.current_tenant_id` per request
  - Added `TenantContextMiddleware` to MIDDLEWARE after `TenantMainMiddleware`
  - Fixed `set_config` parameter from `true` (transaction-local) to `false` (session-persistent)
  - Updated `reset_app.sh` to set RLS context before creating tenant users

**Security Architecture — Final State:**
- Business data isolation: PostgreSQL schemas via django-tenants
- User isolation: PostgreSQL RLS via tenant_isolation policy
- Routing: TenantMainMiddleware
- RLS context: TenantContextMiddleware
- Portal vs Staff routing: PortalMiddleware

**Verified:**
- velton_admin can only see users belonging to Velton tenant
- anciappi (superadmin, tenant=None) visible to all tenants
- Users from other tenants completely invisible across tenant boundaries
- RLS blocks inserts without proper context (confirmed during reset)
- Login flow working correctly with RLS active

**Files Created/Modified:**
- `users/models.py`: added `tenant` FK and `is_superadmin` property
- `core/tenant_context.py`: new TenantContextMiddleware
- `core/settings.py`: added TenantContextMiddleware to MIDDLEWARE
- `core/middleware.py`: added tenant scoping check
- `scripts/rls_setup.sql`: RLS policy, index, FORCE RLS
- `reset_app.sh`: updated with RLS context for user creation

**Pending Tasks — Next:**
- Implement test suite (critical — identified as technical debt)
- QAEngineer: write RLS isolation tests
- QAEngineer: write tenant isolation tests
- Fix hardcoded Spanish URLs in templates (/inventario/ → /inventory/)
- Tailwind CSS refactor — replace hardcoded hex values with tailwind.config.js tokens
- Onboarding flow for new tenants (UI)
- SaaS Super Admin Dashboard (Phase 5)

**Blockers/Open Questions:**
- None.

**RLS — Full Validation Completed:**
- Added `superadmin_bypass` policy to `scripts/rls_setup.sql` — allows superadmin to manage all tenants from global admin
- Added `WITH CHECK` clause to both policies for INSERT/UPDATE protection
- Updated `users/admin.py` — added `tenant` field to Django Admin forms (list, filter, add, edit)

**End-to-End Smoke Test — PASSED:**
- ✅ Superadmin (`anciappi`) manages all tenants from `localhost/admin/`
- ✅ Created new tenant from global admin — schema auto-created correctly
- ✅ Created users and assigned to specific tenants from global admin
- ✅ Each tenant user can only login to their own subdomain
- ✅ Cross-tenant login attempts blocked by RLS
- ✅ Three simultaneous tenant instances operating without interference

**Security Architecture — CLOSED:**
PrintFlow (building)
└── PostgreSQL schemas (django-tenants) → business data isolation
└── RLS policies (PostgreSQL) → user isolation
├── superadmin_bypass → anciappi sees and manages everything
└── tenant_isolation → users see only their tenant
└── TenantMainMiddleware → resolves tenant by subdomain
└── TenantContextMiddleware → sets RLS context per request
└── PortalMiddleware → portal vs staff routing


**Test Suite — RLS Isolation Tests:**
- Created `users/tests/__init__.py` and `users/tests/test_rls.py`
- Created `users/tests/conftest.py` with session-scoped RLS policy fixture
- Created `pytest.ini` in project root
- Granted `CREATEDB` permission to `printflow_user` for test DB creation
- Fixed conftest fixture ordering — `apply_rls_policies` depends explicitly on `django_db_setup`
- Added `usefixtures = apply_rls_policies` to `pytest.ini`

**Final Result: 9/9 tests passing**
- TestRLSSuperadmin::test_superadmin_sees_all_users ✅
- TestRLSSuperadmin::test_superadmin_has_no_tenant ✅
- TestRLSSuperadmin::test_superadmin_is_superadmin_property ✅
- TestRLSTenantIsolation::test_velton_context_sees_only_velton_users ✅
- TestRLSTenantIsolation::test_magtik_context_sees_only_magtik_users ✅
- TestRLSTenantIsolation::test_unknown_tenant_context_sees_only_superadmin ✅
- TestRLSTenantIsolation::test_rls_blocks_cross_tenant_insert ✅
- TestTenantUserProperty::test_tenant_user_is_not_superadmin ✅
- TestTenantUserProperty::test_tenant_user_has_tenant ✅

**Run tests with:**
```bash
pytest users/tests/test_rls.py
```

**Next Session:**
- Expand test suite to other apps (customers, orders, inventory)
- Load/stress test — simulate multiple tenants operating simultaneously
- Fix hardcoded Spanish URLs in templates
- Tailwind CSS refactor
- Onboarding UI flow
- SaaS Super Admin Dashboard (Phase 5)

## Session: 2026-03-17 (continuación tarde)

**Tasks Completed:**
- **RLS Tests — 9/9 passing:** Created `users/tests/test_rls.py`, `users/tests/conftest.py`, `pytest.ini`. Fixed fixture ordering with `apply_rls_policies` depending on `django_db_setup`. Added `usefixtures = apply_rls_policies` to `pytest.ini`. Granted `CREATEDB` to `printflow_user`.
- **URL normalization:** Fixed hardcoded Spanish URLs in 8 templates via `sed`. Verified zero remaining Spanish URL paths.
- **Tailwind CSS refactor:** Replaced all hardcoded hex colors in 33 templates with semantic tokens from `tailwind.config.js`. Added `surface-mid`, `surface-alt`, `surface-deep` tokens (consolidated to `surface-mid`). Fixed CDN config — added `tailwind.config` inline script to `base.html` so custom tokens are recognized by the CDN.

**Files Modified:**
- `users/tests/test_rls.py`, `users/tests/conftest.py`, `pytest.ini`
- 8 templates: Spanish URL paths fixed
- 33 templates: hex colors replaced with tokens
- `tailwind.config.js`: added surface-mid token
- `templates/base.html`: added inline tailwind.config for CDN

**Run tests:**
```bash
pytest users/tests/test_rls.py
```

**Pending:**
- Expand test suite to customers, orders, inventory
- Load/stress test
- CardJobOrder approval flow (UUID token, public URL, standalone template)
- Velton stock import (file pending)
- Onboarding UI
- Super Admin Dashboard (Phase 5)
- Tailwind CLI compilation for production (replace CDN)


Session: 2026-03-18
Tasks Completed:

Tailwind CLI Migration (CDN → CLI v4):

Upgraded Node.js from v18 to v20 LTS via nvm (required by Tailwind v4)
Installed tailwindcss, @tailwindcss/cli, and @tailwindcss/forms via npm
Created static/css/input.css with Tailwind v4 syntax: @import "tailwindcss", @theme block with all 13 custom color tokens, mono font family, sm border radius, and @plugin "@tailwindcss/forms"
Migrated all tokens from tailwind.config.js (v3 syntax) to input.css (v4 @theme syntax)
Compiled static/css/output.css — verified all custom tokens present (--color-surface, --color-surface-dark, etc.)
Updated templates/base.html — removed CDN script and inline tailwind.config block, replaced with <link> to output.css
Added npm run build and npm run watch scripts to package.json
Added node_modules/ and static/css/output.css to .gitignore


Standalone Templates — CDN Removed:

Replaced Tailwind CDN with {% static 'css/output.css' %} link in all standalone templates:
registration/login.html, quotes/portal_login.html, quotes/portal.html,
quotes/quote_form.html, quotes/card_job_form.html, public/landing.html
Fixed CSS regression in card_job_form.html introduced by agent (items-center → align-items: center in <style> block)
Verified zero CDN references remaining: grep -r "cdn.tailwindcss.com" templates/ returns empty


Inline JS Extraction — Static Files:

Created static/js/ directory
Extracted inline JavaScript from 11 templates into 7 modular static files:

toggle-row.js — shared row toggle (used by product_list, consumption_list, inventory_list)
formset.js — shared Django formset handler (used by purchasing/oc_create, inventory/oc_edit) — DRY fix, was duplicated
inventory-modals.js — fraccionar and consumption modals
reception-modal.js — purchase order reception modal
dashboard-toggle.js — inventory dashboard toggle
quote-form.js — delivery toggle and input styling
card-job-form.js — color sync and input styling


All affected templates updated with <script src="{% static 'js/...' %}"> references
Verified: only base.html and product_form.html still contain <script> tags



Architecture Decision — HTMX:

Identified that product_form.html (180 lines of inline JS) and future upload-heavy forms require a scalable solution
Decision: Adopt HTMX to replace custom JS for dynamic interactions project-wide
Rationale: HTMX integrates natively with Django, eliminates JS for 80% of use cases, and enables DRY scalable interactivity
Current JS files are an intermediate state — will be progressively replaced with HTMX
product_form.html JS extraction deferred pending HTMX architecture plan

Files Created/Modified:

package.json, package-lock.json: Node project initialized, Tailwind CLI installed
static/css/input.css: Tailwind v4 entry point with all tokens
static/css/output.css: compiled (gitignored)
templates/base.html: CDN removed, output.css linked
templates/registration/login.html: CDN → output.css
templates/quotes/portal_login.html: CDN → output.css
templates/quotes/portal.html: CDN → output.css
templates/quotes/quote_form.html: CDN → output.css
templates/quotes/card_job_form.html: CDN → output.css, CSS regression fixed
templates/public/landing.html: CDN → output.css
static/js/: 7 new JS files created
11 templates: inline <script> blocks removed, replaced with static file references
.gitignore: added node_modules/ and static/css/output.css

Commits:

feat(frontend): migrate Tailwind CSS from CDN to CLI v4
feat(frontend): replace Tailwind CDN with compiled CSS in standalone templates
refactor(frontend): extract inline JS to static files
chore: add node_modules and output.css to .gitignore

Next Session — HTMX Architecture:

Plan and implement HTMX as the project-wide JS replacement strategy
Define core/ JS library structure for what HTMX cannot cover
Refactor product_form.html (180 lines JS) using HTMX patterns
Unify modal pattern across all apps
Create reusable file-handler.js for upload previews (used in products, card jobs, and future modules)
Create new git branch: feature/htmx-integration

Pending (carried over):

Expand test suite to customers, orders, inventory
CardJobOrder approval flow (UUID token, public URL /aprobar/<uuid>/)
Velton stock import (file pending from client)
Onboarding UI flow
Super Admin Dashboard (Phase 5)