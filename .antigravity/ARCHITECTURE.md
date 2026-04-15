# PrintFlow v2 — Architecture Map

## System Overview
SaaS para gestión de imprentas. Multi-tenant, un schema por cliente.

```
PrintFlow (SaaS)
└── PrintShop/Tenant (imprenta cliente)
    └── Branch (sucursal)
        └── Apps (módulos)
            └── Users (usuarios del tenant)
```

## Tech Stack
- **Backend:** Python 3.12 / Django 6.0.1
- **Database:** PostgreSQL + django-tenants (schemas) + RLS (user isolation)
- **Frontend:** Tailwind CSS v4 CLI + HTMX v2.0.4 + Django Templates
- **Auth:** Django Auth nativo + RLS PostgreSQL
- **Tests:** pytest-django + factory-boy
- **Environment:** .env file, secrets never hardcoded

## Security Architecture
```
Business data isolation  → PostgreSQL schemas (django-tenants)
User isolation          → RLS policies (PostgreSQL)
URL routing             → TenantMainMiddleware (subdomain → tenant)
RLS context             → TenantContextMiddleware (sets app.current_tenant_id)
Portal vs Staff         → PortalMiddleware
Superadmin bypass       → is_superadmin property (tenant=None + is_staff)
```

## Apps and Responsibilities

| App | Schema | Responsibility |
|-----|--------|----------------|
| `tenants` | public | PrintShop, Domain, Branch models |
| `users` | public | User model, RLS isolation |
| `core` | - | Settings, URLs, middleware |
| `customers` | tenant | Customer management |
| `dashboard` | tenant | Metrics and control panel |
| `inventory` | tenant | Materials and stock |
| `orders` | tenant | Work orders lifecycle |
| `products` | tenant | Product and service catalog |
| `purchasing` | tenant | Purchases and suppliers |
| `quotes` | tenant | Portal, quotes, CardJobOrder |

## URL Structure
```
localhost/admin/                → SuperAdmin (public schema)
localhost/login/                → Login (public schema)

velton.localhost/               → Tenant: Grupo Velton
velton.localhost/inventory/     → Inventory module
velton.localhost/purchasing/    → Purchasing module
velton.localhost/customers/     → Customers module
velton.localhost/orders/        → Orders module
velton.localhost/products/      → Products module
velton.localhost/portal/        → Client portal + Staff management
velton.localhost/portal/aprobar/<uuid>/ → Public approval (no login)
```

## Roles
```
SUPERADMIN  → tenant=None, is_staff=True → global access, all tenants
ADMIN       → STAFF role → full dashboard access
MANAGEMENT  → STAFF role → full dashboard access
SALES       → STAFF role → full dashboard access
DESIGNER    → STAFF role → full dashboard access (granular TBD)
TEAM        → STAFF role → full dashboard access (granular TBD)
PORTAL      → CLIENT role → /portal/ only, own orders only
```

## Key Models

### tenants.PrintShop
- schema_name, name, plan
- Related: Domain, Branch

### users.User (public schema, RLS isolated)
- username, email, role, tenant FK
- is_superadmin property → tenant=None + is_staff

### quotes.CardJobOrder (the star module)
- portal_user FK → client ownership
- approval_token UUID → public URL
- status → 8 states workflow
- Related: CardJobColor (Pantone), CardJobFile

### quotes.PantoneColor
- code, hex_value, category
- 373 colors: CMYK + Coated + Metallic + Neon
- Loaded via: python manage.py tenant_command import_pantone --schema=<schema>

## HTMX Patterns Established

### List with partial refresh
```
View.get_template_names() → full page or fragment
hx-trigger="eventName from:body" → refresh on event
HX-Trigger header → fire event after action
```

### Modal pattern
```
hx-get → loads fragment into #modal-container
HttpResponse("") → clears modal
close_modal view → per module
```

### Search/filter
```
hx-get on form → targets list container
hx-trigger="change, keyup changed delay:400ms"
```

## Static Files Structure
```
static/
├── css/
│   ├── input.css      → Tailwind v4 entry (@theme tokens)
│   ├── output.css     → compiled (gitignored)
│   ├── portal.css     → shared styles for standalone templates
│   └── main.css       → legacy
├── js/
│   ├── htmx.min.js    → HTMX v2.0.4
│   ├── sidebar.js     → menu toggle + HTMX state preservation
│   ├── toggle-row.js  → expandable rows (inventory, products)
│   ├── formset.js     → Django formsets (purchasing, inventory)
│   ├── card-job-form.js → color sync (legacy, being replaced by HTMX)
│   └── ...            → other modular files
```

## Development Commands
```bash
# Run server
./runserver.sh  # binds to 0.0.0.0:8001

# Reset everything
./reset_app.sh  # drops DB, recreates, applies migrations, seeds data

# Migrations
python manage.py makemigrations
python manage.py migrate_schemas          # all schemas
python manage.py migrate_schemas --shared # public only

# Import Pantone colors (after reset)
python manage.py tenant_command import_pantone --schema=velton

# Tests
pytest users/tests/test_rls.py      # RLS isolation tests
pytest quotes/tests/                 # portal security tests

# Tailwind
npm run build   # compile once
npm run watch   # watch mode
```

## Module Status
```
inventory   ✅ HTMX complete, fragments, modal patterns established
purchasing  ✅ HTMX complete
orders      ✅ Rediseño "Dark Industrial" completo, layout 7xl, modal de avance con desglose por etapa.
products    ✅ functional (product_form.html JS extraction pending)
quotes      🔄 backend complete, card_job_form UI in progress
customers   ✅ functional
tenants     ✅ multi-tenant operational (Grupo Velton: Velton + Magtik)
users       ✅ RLS active, 24/24 tests passing
```

## Pending — MVP
1. card_job_form.html — dark theme + Django + HTMX
2. Superadmin full portal access (partial fix done)
3. card_job_detail.html — verify with real data
4. Super Admin Dashboard (Phase 5)
5. CardJobOrder approval flow — UUID public URL
