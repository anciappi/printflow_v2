
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


Session: 2026-03-18 (continuación noche)
Tasks Completed:

HTMX — Instalación y configuración base:

Instalado django-htmx — agregado a SHARED_APPS y MIDDLEWARE
Descargado htmx.min.js v2.0.4 a static/js/
Cargado en base.html antes de </body>
hx-boost="true" agregado y luego removido del <body> — demasiado agresivo mientras no todos los templates estén adaptados


HTMX — Módulo Inventory (primer módulo migrado):

Creadas 3 views de fragment en inventory/views.py:

ConsumoModalView — GET devuelve modal de consumo
FraccionarModalView — GET devuelve modal de fraccionar
RecepcionModalView — GET devuelve modal de recepción OC


Creada close_modal view — devuelve HttpResponse("") para cerrar modales
Registradas 4 nuevas URLs en inventory/urls.py:

consumo/<int:unit_id>/modal/
fraccionar/<int:unit_id>/modal/
remitos/<int:pk>/modal/
modal/close/


Creada carpeta templates/inventory/fragments/ con 4 fragments:

consumo_modal.html — modal HTMX con datos del servidor, sin JS
fraccionar_modal.html — modal HTMX con datos del servidor, sin JS
recepcion_modal.html — modal HTMX con datos del servidor, sin JS
inventory_table.html — tabla de inventario para refresh parcial


Actualizadas views registrar_consumo, fraccionar_unidad, recibir_oc:

Si request.htmx → devuelve HttpResponse("") + HX-Trigger header
Si error → devuelve fragment con mensaje de error inline
Flujo normal (redirect) preservado intacto


InventoryListView actualizado con get_template_names() — devuelve fragment si HTMX, página completa si browser
inventory_list.html refactorizado — wrapper con hx-trigger="inventoryUpdated from:body" + {% include %} del fragment
Eliminados modales estáticos de inventory_list.html y purchaseorder_list.html
Eliminados inventory-modals.js y reception-modal.js del proyecto (reemplazados por HTMX)



Resultado:

✅ Modal de consumo funciona — abre con datos reales, procesa, cierra y actualiza lista sin recargar
✅ Modal de fraccionar funciona
✅ Navegación desde sidebar funciona correctamente
✅ Descuento refleja cantidad correcta inmediatamente

Architecture Decision — hx-boost:

hx-boost="true" removido del <body> — se reactivará cuando todos los módulos estén migrados a HTMX
Estrategia: migrar módulo por módulo, reactivar boost al final

Files Created/Modified:

inventory/views.py: 4 nuevas views, 3 views actualizadas con request.htmx
inventory/urls.py: 4 nuevas URLs
templates/inventory/fragments/: 4 nuevos fragments
templates/inventory/inventory_list.html: refactorizado para HTMX
templates/inventory/purchaseorder_list.html: modales estáticos removidos
static/js/htmx.min.js: descargado
templates/base.html: htmx.min.js cargado, hx-boost removido
core/settings.py: django-htmx en SHARED_APPS y MIDDLEWARE
requirements.txt: django-htmx agregado

Commits:

feat(htmx): install and configure HTMX v2.0.4
(pending commit de inventory HTMX migration)


Pendientes — Próxima Sesión
🔴 Bugs críticos

Bug deshacer_fraccionamiento — cuando se deshace un corte, la unidad padre se resetea a cantidad original ignorando consumos realizados sobre las unidades hijas. Afecta integridad de datos. Investigar deshacer_fraccionamiento() en el modelo InventoryUnit.

🟠 HTMX — Continuar migración

Cerrar modal no resetea el desplegable — al refrescar #inventory-list después de un consumo, el estado del toggle (filas expandidas) se pierde. Solución: guardar estado del toggle en JS antes del refresh y restaurarlo después con htmx:afterSwap event.
Migrar módulo purchasing — mismo patrón que inventory
Migrar módulo orders — mismo patrón
Migrar módulo products — mismo patrón
Migrar módulo quotes — mismo patrón
product_form.html — 180 líneas JS, separar en product-colors.js y file-handler.js (core/)
Reactivar hx-boost — una vez que todos los módulos estén migrados

🟡 Deuda técnica frontend

CSS inline en templates — extraer bloques <style> restantes a Tailwind o static/css/
Sidebar state — al navegar, el menú activo se colapsa (efecto secundario de HTMX navigation)
base.html script inline — JS de sidebar está inline, extraer a static/js/sidebar.js

🟢 Features pendientes

Super Admin Dashboard (Fase 5) — gestionar tenants, branches y usuarios desde UI
CardJobOrder approval flow — UUID token, URL pública /aprobar/<uuid>/
Velton stock import — archivo pendiente del cliente
Onboarding UI flow — para nuevos tenants
Expandir suite de tests — customers, orders, inventory


Session: 2026-03-19
Tasks Completed:

HTMX Migration — Completada al 100%:
Inventory (completado sesión anterior, verificado hoy):

Fragment views: ConsumoModalView, FraccionarModalView, RecepcionModalView, close_modal
Views actualizadas con request.htmx: registrar_consumo, fraccionar_unidad, recibir_oc, delete_purchase_order, eliminar_consumo
Fragments: consumo_modal.html, fraccionar_modal.html, recepcion_modal.html, inventory_table.html
InventoryListView con get_template_names() para respuesta parcial HTMX
Confirms de eliminación migrados a hx-confirm nativo

Purchasing:

Fragment views: RecepcionModalView, close_modal
Views actualizadas: recibir_oc, delete_purchase_order
Fragments: recepcion_modal.html, oc_table.html
PurchaseOrderListView con get_template_names()
Modal estático y JS confirms eliminados de purchaseorder_list.html

Orders: ✅ Limpio desde el inicio — nació con arquitectura correcta
Products: ✅ product_list.html usa toggle-row.js — correcto. product_form.html tiene JS legítimo (FileReader API, DOM manipulation) — deuda técnica frontend, no HTMX
Quotes: ✅ Limpio — sin JS inline
Sidebar JS extraído:

Creado static/js/sidebar.js con toggleMenu, activateSidebarByPath
Agregados htmx:beforeSwap y htmx:afterSwap listeners para preservar estado de filas expandidas
Eliminado script inline de base.html


hx-boost — Decisión arquitectónica:

Evaluado y descartado deliberadamente
Razones: templates standalone incompatibles, ganancia marginal para SaaS interno, HTMX quirúrgico ya implementado donde agrega valor real
Decisión final: no se implementa hx-boost en este proyecto



Architecture Decisions Logged:

DRY es innegociable — cualquier lógica que se repite 2+ veces se extrae. Sin excepciones.
HTMX pattern estándar del proyecto:

View con get_template_names() — página completa vs fragment
Fragment en templates/<app>/fragments/
hx-trigger="<event> from:body" en el wrapper de la lista
HX-Trigger header en el response para disparar refresh
close_modal view reutilizable por módulo


JS legítimo vs JS a eliminar:

JS legítimo: FileReader API, manipulación de DOM compleja, estado de UI puro
JS a eliminar: confirms, modales, form actions, fetch/ajax


hx-boost descartado — no agrega valor suficiente vs complejidad que introduce

Files Created/Modified:

inventory/views.py: 4 nuevas views, 5 views actualizadas
inventory/urls.py: 4 nuevas URLs
purchasing/views.py: 2 nuevas views, 2 views actualizadas
purchasing/urls.py: 2 nuevas URLs
templates/inventory/fragments/: consumo_modal.html, fraccionar_modal.html, recepcion_modal.html, inventory_table.html
templates/purchasing/fragments/: recepcion_modal.html, oc_table.html
templates/inventory/inventory_list.html: refactorizado para HTMX
templates/inventory/purchaseorder_list.html: modales y JS eliminados
templates/purchasing/purchaseorder_list.html: modales y JS eliminados
static/js/sidebar.js: creado con toggle, auto-activate y HTMX state preservation
templates/base.html: script inline eliminado, sidebar.js cargado

Commits:

feat(htmx): complete inventory module HTMX migration
feat(htmx): migrate purchasing module to HTMX
feat(htmx): complete HTMX migration across all modules
refactor(frontend): extract sidebar JS and add HTMX toggle state preservation


Próximo Sprint — Deuda Técnica Frontend
🔴 Prioridad Alta

product_form.html — Separar JS en archivos modulares:

static/js/product-colors.js — lógica de colores (addColorRow, removeColorRow, syncColors)
static/js/core/file-handler.js — previews y marcado de archivos (reutilizable en todo el proyecto)
Crear carpeta static/js/core/ para utilidades compartidas


CSS inline restante — Auditar y extraer:

Identificar templates con bloques <style> hardcodeados
Migrar a clases Tailwind o static/css/


base.html — Verificar limpieza completa

🟠 Prioridad Media

Sidebar state — menú activo se colapsa al navegar entre secciones (efecto secundario menor)
Toggle state después de consumo — filas expandidas se cierran al refrescar lista (sidebar.js ya tiene el listener, verificar funcionamiento)

🟢 Features — Post limpieza

Super Admin Dashboard (Fase 5) — gestionar tenants, branches y usuarios desde UI
CardJobOrder approval flow — UUID token, URL pública /aprobar/<uuid>/
Bug deshacer_fraccionamiento — unidad padre se resetea ignorando consumos de hijas
Velton stock import — archivo pendiente del cliente
Onboarding UI flow — para nuevos tenants
Expandir suite de tests — customers, orders, inventory



## Session: 2026-03-19 (continuación — cierre Sprint 2)

**Sprint 2 — Deuda Técnica Frontend: CERRADO ✅**

**Tasks Completed:**

- **Portal CSS Unificado:**
  - Creado `static/css/portal.css` — estilos compartidos para todos los templates standalone del portal
  - Eliminados bloques `<style>` inline de 4 templates: `portal_login.html`, `portal.html`, `quote_form.html`, `card_job_form.html`
  - `.custom-scrollbar` migrado a `portal.css` con CSS variables (`var(--color-surface-dark)`, `var(--color-border-default)`)
  - `card_job_detail.html` limpiado — bloque `<style>` con `@apply` inválido eliminado

- **`card_job_detail.html` — Decisión arquitectónica:**
  - Template marcado para **reconstrucción completa** — nuevo diseño aprobado por cliente
  - Nuevo diseño incluye: gestión de tintas Pantone, preview de imágenes con zoom, upload drag & drop, firma digital, especificaciones técnicas, flujo de aprobación completo
  - No se invierte más tiempo en el template actual

- **`product_form.html` — Deuda técnica diferida:**
  - 180 líneas de JS legítimo (FileReader API, DOM manipulation)
  - Se extrae en próximo sprint dedicado: `static/js/product-colors.js` + `static/js/core/file-handler.js`
  - `core/` será la librería JS interna reutilizable del proyecto

**Architecture Decisions Logged:**
- **DRY es innegociable** — cualquier lógica que se repite 2+ veces se extrae sin excepciones
- **CSS inline = deuda técnica** — todo CSS va a archivos estáticos con tokens semánticos
- **`@apply` solo en archivos compilados** — nunca en `<style>` tags inline
- **No reconstruir lo que va a ser reemplazado** — decisión pragmática sobre `card_job_detail.html`

**Files Created/Modified:**
- `static/css/portal.css`: creado con estilos unificados del portal
- `templates/quotes/portal_login.html`: `<style>` eliminado, `portal.css` vinculado
- `templates/quotes/portal.html`: `<style>` eliminado, `portal.css` vinculado
- `templates/quotes/quote_form.html`: `<style>` eliminado, `portal.css` vinculado
- `templates/quotes/card_job_form.html`: `<style>` eliminado, `portal.css` vinculado
- `templates/quotes/card_job_detail.html`: `<style>` con `@apply` eliminado

**Commits:**
- `refactor(frontend): complete Sprint 2 - frontend technical debt`

---

## Estado del Proyecto — Post Sprint 1 y 2

**Infraestructura:**
- ✅ Multi-tenant con django-tenants (schemas PostgreSQL)
- ✅ RLS PostgreSQL — aislamiento de usuarios a nivel DB
- ✅ 9/9 tests RLS pasando
- ✅ Tailwind CLI v4 — CSS compilado, sin CDN
- ✅ HTMX v2.0.4 — interacciones parciales sin JS custom
- ✅ JS modularizado en `static/js/`
- ✅ CSS unificado en `static/css/`
- ✅ SESSION_LOG completo

**Módulos operativos:**
- ✅ Inventory — HTMX completo
- ✅ Purchasing — HTMX completo
- ✅ Orders — limpio desde el inicio
- ✅ Products — funcional (product_form.html pendiente JS extraction)
- ✅ Quotes — portal funcional (card_job_detail.html pendiente reconstrucción)
- ✅ Customers — funcional
- ✅ Users + Auth — RLS activo
- ✅ Tenants — multi-tenant operativo (Grupo Velton: Velton + Magtik)

---

## Próximo Sprint — MVP para presentación

### 🔴 Crítico para MVP
1. **`card_job_detail.html` — Reconstrucción completa** desde nuevo diseño aprobado
   - Gestión de tintas Pantone (agregar/eliminar)
   - Preview de imágenes anverso/reverso con zoom
   - Upload drag & drop para archivos originales
   - Firma digital integrada
   - Especificaciones técnicas en tabla
   - Flujo de aprobación completo
   - URL pública `/aprobar/<uuid>/` para cliente externo

2. **Super Admin Dashboard (Fase 5)** — gestionar tenants, branches y usuarios desde UI

3. **CardJobOrder approval flow** — UUID token, notificación, standalone template

### 🟠 Post-MVP inmediato
4. **`product_form.html`** — extraer JS en `product-colors.js` y `core/file-handler.js`
5. **Bug `deshacer_fraccionamiento`** — unidad padre se resetea ignorando consumos de hijas
6. **Velton stock import** — archivo pendiente del cliente
7. **Sidebar state** — menú activo se colapsa al navegar

### 🟢 Backlog
8. **Expandir suite de tests** — customers, orders, inventory
9. **Onboarding UI flow** — para nuevos tenants
10. **Load/stress test** — múltiples tenants simultáneos
11. **Tailwind CLI para producción** — configurar build en deploy


Session: 2026-03-20
Sprint CardJob-1 — Modelos base: CERRADO ✅
Sprint CardJob-2 — Flujo de estados y vistas: CERRADO ✅
Sprint Seguridad Portal — En progreso 🔄
Tasks Completed:

CardJob Sprint 1 — Modelos extendidos:

PantoneColor model — librería de colores con CMYK + Pantone Coated/Metallic/Neon
CardJobColor model — gestión de tintas por cara (FRONT/BACK)
CardJobFile model — archivos por tipo (FRONT/BACK/DIECUT/TECH)
Campos nuevos en CardJobOrder: approval_token, quantity, unit_price, delivery_address, estimated_delivery
STATUS_CHOICES expandido a 8 estados: DRAFT → SUBMITTED → STAFF_REVIEW → PENDING_CLIENT → APPROVED/APPROVED_WITH_CHANGES/REJECTED → IN_PRODUCTION
max_length corregido en status field (20→30) para cubrir APPROVED_WITH_CHANGES
Management command import_pantone — 373 colores importados en schema velton
Filtros y búsqueda en CardJobOrderListView (q, status, branch, date_from, date_to)
Migraciones aplicadas en todos los schemas


CardJob Sprint 2 — Flujo de aprobación:

Permission mixins refactorizados: PortalClientMixin, StaffMixin, PortalOrStaffMixin
5 vistas de transición de estados:

CardJobSubmitView: DRAFT → SUBMITTED
CardJobStaffReviewView: SUBMITTED → STAFF_REVIEW
CardJobSendToClientView: STAFF_REVIEW → PENDING_CLIENT
CardJobClientApprovalView: aprobación pública via UUID token
CardJobToProductionView: APPROVED → IN_PRODUCTION


URL pública /aprobar/<uuid>/ sin login requerido
Todas las vistas con soporte HTMX (HX-Trigger: jobUpdated)
card_job_list.html actualizado con filtros HTMX y 8 badges de estado
templates/quotes/fragments/job_table.html creado


Sprint Seguridad Portal:

Arquitectura de roles definida: PORTAL (clientes) vs STAFF (todos los demás roles)
PortalMiddleware simplificado — PORTAL solo a /portal/, STAFF sin restricciones
portal_user FK agregado a CardJobOrder — ownership robusto vs chequeo por email frágil
CardJobOrderDetailView actualizado — chequeo via portal_user FK
CardJobOrderCreateView — auto-vincula orden al portal_user en creación
PortalView — muestra solo órdenes del usuario autenticado
PortalCreateUserView — staff crea acceso portal con password auto-generado
factory-boy instalado
Suite de tests creada: quotes/tests/ con 15 tests de seguridad
Tests fallan por falta de configuración de tenant context — fix pendiente



Architecture Decisions Logged:

PORTAL vs STAFF — dos mundos completamente separados, mismo tenant
Un usuario por cliente — no credenciales genéricas compartidas
Permisos granulares de staff — definidos post-MVP por cada imprenta
UUID token — solo para aprobación pública, no para carga de solicitudes
Credenciales portal — staff crea el usuario, password generado automáticamente
Catálogos base del sistema — PantoneColor es el primero, se expande a materiales e insumos post-MVP

Files Created/Modified:

quotes/models.py: PantoneColor, CardJobColor, CardJobFile, CardJobOrder extendido
quotes/views.py: mixins, 5 vistas de transición, PortalCreateUserView, PortalView
quotes/urls.py: URLs de transición + aprobación pública + portal_create_user
quotes/management/commands/import_pantone.py: comando de importación
core/middleware.py: PortalMiddleware simplificado
quotes/tests/: init.py, factories.py, test_portal_security.py
templates/quotes/card_job_list.html: filtros HTMX + badges actualizados
templates/quotes/fragments/job_table.html: fragment para HTMX
requirements.txt: factory-boy agregado
Migraciones: quotes.0003 (modelos nuevos), quotes.0004 (portal_user FK)

Commits:

feat(quotes): CardJob Sprint 1 - extended models and Pantone library
feat(quotes): CardJob Sprint 2 - approval workflow views and URLs
feat(quotes): card_job_list with HTMX filters and updated status badges
security(portal): role isolation and portal user architecture
test(quotes): add portal security test suite - setup pending


Próxima Sesión — Pendientes
🔴 Inmediato

Fix tests de seguridad — configurar tenant context en quotes/tests/conftest.py

Los 15 tests están escritos y correctos
Solo falta el setup del entorno de tenant para que corran
Objetivo: 15/15 tests passing


portal_create_user.html — template para que staff cree usuarios portal

Vista ya existe, falta el template



🟠 Sprint CardJob-3 — UI completa

Reconstrucción completa card_job_detail.html — nuevo diseño aprobado

Gestión de tintas Pantone con HTMX
Upload de archivos por cara
Especificaciones técnicas
Sección de aprobación


card_job_approval.html — template público standalone para cliente
card_job_approval_success.html — confirmación post-aprobación

🟢 Post-MVP

Catálogos base del sistema — materiales, insumos (mismo patrón que PantoneColor)
Permisos granulares por rol de staff — definidos con cada cliente
Mail automático — envío de credenciales portal al cliente
Documentación técnica — para developers
Tutoriales para usuarios — para clientes finales
Dark/Light theme — post-MVP


## Session: 2026-03-20 (continuación — cierre Sprint Seguridad)

**Sprint Seguridad Portal: CERRADO ✅**
**Tests de Seguridad: 15/15 PASSING ✅**

**Tasks Completed:**

- **Fix suite de tests — 15/15 passing:**
  - Creado `quotes/tests/conftest.py` con tenant context, RLS policies y fixtures
  - `auth_client` fixture — crea sesión manualmente dentro del tenant schema
  - `tenant` fixture — crea schema de test con RLS configurado
  - `set_tenant_context` fixture — activa tenant en cada test automáticamente
  - Factories actualizadas — `tenant` asignado en todos los usuarios de prueba
  - Aserciones ajustadas — aceptan 302 y 403 como respuestas válidas de acceso denegado
  - Instalado `factory-boy`
  - `portal_create_user.html` — template creado
  - `card_job_detail.html` — placeholder creado (reconstrucción completa en Sprint CardJob-3)

- **Resultados finales:**
  - TestPortalUserAccess — 5/5 ✅
  - TestStaffUserAccess — 3/3 ✅
  - TestCardJobOwnership — 4/4 ✅
  - TestPortalCreateUser — 3/3 ✅

**Warnings menores pendientes (no críticos):**
- `DeprecationWarning` factory-boy — agregar `skip_postgeneration_save=True` en factories
- `UnorderedObjectListWarning` inventory — agregar `ordering` en queryset de Material

**Architecture Decisions — Sprint Seguridad (CERRADO):**
- PORTAL → solo `/portal/*`, nunca dashboard
- STAFF → acceso total, sin restricciones de URL
- Un usuario por cliente — creado por staff con password auto-generado
- Ownership via `portal_user` FK — robusto vs chequeo por email
- 403 y 302 son ambos válidos como "acceso denegado" — 403 es más correcto para `UserPassesTestMixin`

**Files Created/Modified:**
- `quotes/tests/conftest.py`: tenant context + RLS + auth_client fixture
- `quotes/tests/factories.py`: tenant asignado en factories
- `quotes/tests/test_portal_security.py`: 15 tests, aserciones ajustadas
- `templates/quotes/portal_create_user.html`: template creado
- `templates/quotes/card_job_detail.html`: placeholder creado

**Commits:**
- `test(quotes): 15/15 security tests passing`

---

## Estado del Proyecto — Fin de sesión 2026-03-20

**Sprints cerrados hoy:**
- ✅ CardJob Sprint 1 — Modelos extendidos + Pantone library
- ✅ CardJob Sprint 2 — Flujo de aprobación + vistas de transición
- ✅ Sprint Seguridad Portal — Roles, middleware, ownership, 15/15 tests

**Base técnica actual:**
- ✅ Multi-tenant con RLS
- ✅ HTMX en todos los módulos
- ✅ JS modularizado
- ✅ CSS unificado
- ✅ Tailwind CLI v4
- ✅ 24/24 tests pasando (9 RLS + 15 seguridad portal)
- ✅ Flujo de aprobación CardJob — backend completo
- ✅ Aislamiento PORTAL/STAFF verificado y testeado

---

## Próximo Sprint — CardJob Sprint 3 — UI completa

### 🔴 Core del MVP
1. **`card_job_detail.html`** — reconstrucción completa con nuevo diseño
   - Metadata de orden (read-only para PORTAL, editable para STAFF)
   - Gestión de tintas Pantone con HTMX (agregar/eliminar)
   - Upload de archivos por cara (FRONT/BACK/DIECUT/TECH)
   - Especificaciones técnicas en tabla
   - Sección de aprobación con 3 opciones
   - Botones de transición de estado según rol

2. **`card_job_approval.html`** — template público standalone
   - Sin login — acceso por UUID token
   - Dark theme, standalone (no extiende base.html)
   - 3 opciones: Aprobado / Aprobado con cambios / Rechazado
   - Campo firma y cargo

3. **`card_job_approval_success.html`** — confirmación post-aprobación

4. **`portal_create_user.html`** — mejorar template actual (placeholder)

### 🟠 Warnings menores a limpiar
5. `skip_postgeneration_save=True` en factories
6. `ordering` en queryset de Material (inventory)

### 🟢 Post-MVP
7. Mail automático de credenciales al cliente
8. Catálogos base del sistema (materiales, insumos)
9. Permisos granulares por rol de staff
10. Dark/Light theme
11. Documentación técnica + tutoriales para usuarios

## Session: 2026-04-07
**Tasks Completed:**
- **WorkOrder Detail UI Polish**: Reestructuración y modernización de `workorder_detail.html` para cumplir con el estilo "Dark Industrial". Integración de las acciones y botones al nivel del encabezado, remoción de paneles redundantes, y conversión de la etiqueta de "Estado de Producción" en un componente compacto.
- **Trazabilidad & Ficha Médica**: Adaptación visual completa de la tabla de logs de producción `log_feed.html` heredando el estilo implementado en el componente de consumos, logrando alta densidad de información.
- **Optimización de Interfaz Dinámica**: Conversión de `product_details.html` a un componente de tabla condicional que oculta los atributos falsos, limpiando drásticamente el espacio vertical del formulario.
- **Grillas Asimétricas**: Rediseño integral de `workorder_form.html` introduciendo un grid de 2 columnas donde los componentes anchos (Configuración de Postura) conviven en un balance 50/50 con las tarjetas estrechas (Cronograma y Observaciones), optimizando la densidad de la pantalla y arreglando bugs previos de overflow (`</div>` erróneos inyectados por HTMX).
- **HTMX Architecture - JS Extraction**: Se identificó un anti-patrón de arquitectura donde la calculadora de materiales estaba hardcodeada en el bloque de scripts del template de `workorder_form.html`. Se extrajo exitosamente a un archivo externo estático modular (`static/js/workorder_layout_preview.js`) con una robusta inyección global de estado y estrategias auto-gestionadas de "cache busting".

**Files Created/Modified:**
- `templates/orders/workorder_detail.html`: Refactorización de layout.
- `templates/orders/workorder_form.html`: Rejilla asimétrica y extracción de script.
- `templates/orders/fragments/log_feed.html`: Remasterización de tabla Dark Industrial.
- `templates/orders/fragments/product_details.html`: Limpieza visual condicional. Modificado bug de div huérfano.
- `templates/orders/fragments/status_badge.html`: Modificación a layout de pastilla compacta.
- `static/js/workorder_layout_preview.js`: **[NUEVO]** Script estático e independiente extraído desde los dominios del template.
- `.antigravity/logs/log-orders.md`: Adición del registro del sprint actual.