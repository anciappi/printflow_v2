# Skill: PortalDeveloper — PrintFlow v2

## Role
Portal and client-facing module specialist for PrintFlow v2.
You own everything related to the client portal, approval flows, and client-staff interaction.

## Before starting ANY task
1. Read `.antigravity/rules.md`
2. Read `.antigravity/logs/log-quotes.md`
3. Read `.antigravity/STYLE_GUIDE.md`

## What you own
- `quotes/` app — all views, models, forms, URLs
- `templates/quotes/` — all portal templates
- Client portal flow — from submission to approval to production
- Pantone color management — HTMX endpoints
- CardJobOrder lifecycle — all status transitions

## The portal architecture

### Two worlds, same tenant
```
PORTAL users  → /portal/* only
STAFF users   → full access including /portal/
SUPERADMIN    → global access, no restrictions
```

### Permission mixins (always use these)
```python
class StaffMixin(UserPassesTestMixin):
    """Any role except PORTAL."""
    def test_func(self):
        return self.request.user.role != User.Roles.PORTAL

class PortalClientMixin(UserPassesTestMixin):
    """PORTAL role only."""
    def test_func(self):
        return self.request.user.role == User.Roles.PORTAL

class PortalOrStaffMixin(UserPassesTestMixin):
    """Any authenticated user."""
    def test_func(self):
        return self.request.user.is_authenticated
```

### CardJobOrder status flow
```
DRAFT
  → SUBMITTED          (client or staff)
  → STAFF_REVIEW       (staff takes it)
  → PENDING_CLIENT     (staff sends to client)
  → APPROVED           (client approves)
  → APPROVED_WITH_CHANGES
  → REJECTED
  → IN_PRODUCTION      (staff sends to production)
```

### URL structure
```python
# Portal (client-facing)
/portal/login/                          → PortalLoginView
/portal/                                → PortalView (client home)
/portal/card-job/new/                   → CardJobOrderCreateView
/portal/card-job/<pk>/                  → CardJobOrderDetailView
/portal/users/new/                      → PortalCreateUserView (staff)

# Workflow transitions
/portal/card-job/<pk>/submit/           → CardJobSubmitView
/portal/card-job/<pk>/staff-review/     → CardJobStaffReviewView
/portal/card-job/<pk>/send-to-client/   → CardJobSendToClientView
/portal/card-job/<pk>/to-production/    → CardJobToProductionView

# Public (no login)
/portal/aprobar/<uuid>/                 → CardJobClientApprovalView

# Color management (HTMX)
/portal/pantone/search/                 → PantoneSearchView
/portal/card-job/<pk>/color/add/        → CardJobColorAddView
/portal/card-job/<pk>/color/<pk>/remove/ → CardJobColorRemoveView
```

### Template types in quotes
```
templates/quotes/
├── portal_login.html          → standalone, client login
├── portal.html                → standalone, client home
├── card_job_form.html         → standalone, order creation/edit
├── card_job_detail.html       → extends base.html, staff view
├── card_job_list.html         → extends base.html, staff list
├── card_job_approval.html     → standalone, public UUID approval
├── card_job_approval_success.html → standalone, post-approval
├── portal_create_user.html    → extends base.html, staff creates client
└── fragments/
    ├── job_table.html         → HTMX partial for list
    ├── color_list.html        → HTMX color management
    └── pantone_search_results.html → HTMX Pantone search
```

### Standalone templates load
```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
  <link rel="stylesheet" href="{% static 'css/output.css' %}">
  <link rel="stylesheet" href="{% static 'css/portal.css' %}">
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet"/>
  <script src="{% static 'js/htmx.min.js' %}"></script>
</head>
<body class="min-h-screen bg-surface-dark antialiased text-slate-300">
```

### Pantone color management
```python
# Search — returns fragment
PantoneSearchView → GET ?q=<query>&side=FRONT&job_pk=<pk>
                  → renders fragments/pantone_search_results.html

# Add color
CardJobColorAddView → POST {pantone_id, side}
                    → renders fragments/color_list.html

# Remove color
CardJobColorRemoveView → POST
                       → renders fragments/color_list.html
```

### Client user creation
```python
# Staff creates portal user
PortalCreateUserView.post():
    - email + full_name required
    - auto-generates 12-char password
    - role = PORTAL, tenant = request.tenant
    - shows password ONCE — never stored in plain text
```

## What to never do
- Never let PORTAL users access staff views
- Never show unit_price to PORTAL users
- Never allow cross-tenant data access
- Never bypass ownership check on CardJobOrder
- Never use email as ownership check — use portal_user FK
