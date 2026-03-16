
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
- **First Real Tenant (Phase 2):** Created `Velton` tenant with `schema_name='velton'` mapped to `velton.localhost`. Verified 17 isolated business tables in `velton` schema.
- **Branch Promoted to Central Concept:** Moved `Branch` model from `inventory` to `tenants`. Added FK to `Branch` in `WorkOrder` (required), `QuoteRequest` (required), `CardJobOrder` (nullable — assigned by staff after client submits portal form). Updated `purchasing` and `inventory` references accordingly. Applied all migrations to both `public` and `velton` schemas.

**Architecture decisions logged:**
- Building analogy: PrintFlow (building) → PrintShop/tenant (floor) → Branch (department) → Apps (rooms) → Users (tenants)
- Shared data within tenant: customers, materials, products, suppliers
- Branch-scoped data: work orders, quotes, card job orders
- CardJobOrder.branch is nullable: client submits externally, branch assigned on staff approval
- Superadmin lives in public schema, operational users live in tenant schema

**Files Created/Modified:**
- `tenants/`: `models.py`, `admin.py`
- `core/`: `settings.py`, `urls.py`, `urls_public.py`
- `inventory/models.py`: removed local Branch, added import from tenants
- `orders/models.py`: added Branch FK
- `quotes/models.py`: added Branch FK to QuoteRequest and CardJobOrder
- `purchasing/models.py`: updated Branch reference
- `requirements.txt`: added django-tenants==3.7.0

**Next Pending Tasks:**
- Phase 3: Rewrite PortalMiddleware for multi-tenant + portal routing
- Phase 3: Configure /etc/hosts for local tenant development
- Phase 4: Full functional validation smoke test
- Create Magtik branch under Grupo Velton tenant
- Build onboarding flow for new tenants

**Blockers/Open Questions:**
- None.
