# Log: quotes — PrintFlow v2

Módulo responsable de: portal de clientes, presupuestos, CardJobOrder, flujo de aprobación.

---

## Sprint: Portal inicial | 2026-03-07 | CERRADO ✅
- Diseño portal_login.html, portal.html, quote_form.html — estética High-Tech
- Modelo CardJobOrder implementado en quotes/models.py
- CardJobOrderClientForm + CardJobOrderStaffForm
- Templates: card_job_form.html, card_job_detail.html, card_job_list.html
- PortalMiddleware — acceso no autenticado a /portal/login/

## Sprint: CardJob-1 Modelos | 2026-03-20 | CERRADO ✅
- PantoneColor model — 373 colores (CMYK + Coated + Metallic + Neon)
- CardJobColor model — tintas por cara (FRONT/BACK)
- CardJobFile model — archivos por tipo (FRONT/BACK/DIECUT/TECH)
- CardJobOrder extendido:
  - approval_token (UUID, único)
  - quantity, unit_price
  - delivery_address, estimated_delivery
  - STATUS_CHOICES → 8 estados
  - portal_user FK
- Management command import_pantone — 373 colores en schema velton
- CardJobOrderListView con filtros: q, status, branch, date_from, date_to
- Migraciones: quotes.0003, quotes.0004

## Sprint: CardJob-2 Flujo | 2026-03-20 | CERRADO ✅
- Permission mixins: StaffMixin, PortalClientMixin, PortalOrStaffMixin
- Vistas de transición:
  - CardJobSubmitView: DRAFT → SUBMITTED
  - CardJobStaffReviewView: SUBMITTED → STAFF_REVIEW
  - CardJobSendToClientView: STAFF_REVIEW → PENDING_CLIENT
  - CardJobClientApprovalView: aprobación pública UUID
  - CardJobToProductionView: APPROVED → IN_PRODUCTION
- URL pública: /portal/aprobar/<uuid>/
- HTMX: HX-Trigger en todas las vistas de transición
- card_job_list.html: filtros HTMX + 8 badges de estado
- fragments/job_table.html creado

## Sprint: Seguridad Portal | 2026-03-20 | CERRADO ✅
- PortalMiddleware simplificado: PORTAL solo /portal/, STAFF sin restricciones
- portal_user FK en CardJobOrder — ownership robusto
- CardJobOrderDetailView: chequeo via portal_user FK
- CardJobOrderCreateView: auto-vincula al portal_user
- PortalView: muestra solo órdenes del usuario autenticado
- PortalCreateUserView: staff crea acceso con password auto-generado
- 15/15 tests de seguridad pasando (quotes/tests/)

## Sprint: Pantone HTMX | 2026-03-21 | CERRADO ✅
- PantoneSearchView: búsqueda filtrada, máximo 20 resultados
- CardJobColorAddView: agrega tinta con chequeo de ownership
- CardJobColorRemoveView: elimina tinta con chequeo de ownership
- URLs: pantone/search/, card-job/<pk>/color/add/, color/<pk>/remove/
- fragments/color_list.html creado
- fragments/pantone_search_results.html creado
- CardJobOrderClientForm: campos de color removidos — manejados via HTMX
- CardJobOrderCreateView: redirige al detail post-creación

## Sprint: card_job_form UI | 2026-03-21 | 🔄 EN PROGRESO
**Estado:** Diseño HTML disponible en .antigravity/customers.html
**Pendiente:**
- Convertir a dark theme usando tokens STYLE_GUIDE.md
- Conectar variables Django del modelo CardJobOrder
- Implementar HTMX para tintas Pantone
- Eliminar CSS/JS hardcodeado
- Verificar roles PORTAL vs STAFF
**Estrategia:** sección por sección, verificar en browser antes de commitear
**Archivos a tocar:** templates/quotes/card_job_form.html ÚNICAMENTE

## Pendientes del módulo
1. card_job_form.html UI — dark theme + Django + HTMX (EN PROGRESO)
2. card_job_detail.html — verificar con datos reales en browser
3. Superadmin acceso completo al portal (fix parcial en middleware)
4. card_job_approval.html — revisar con datos reales
5. portal_create_user.html — mejorar diseño placeholder

## Archivos del módulo
```
quotes/
├── models.py          → QuoteRequest, PantoneColor, CardJobColor, CardJobFile, CardJobOrder
├── views.py           → todas las vistas del portal
├── forms.py           → CardJobOrderClientForm, CardJobOrderStaffForm
├── urls.py            → todas las URLs bajo /portal/
├── admin.py
└── management/commands/import_pantone.py

templates/quotes/
├── portal_login.html
├── portal.html
├── card_job_form.html         ← UI pendiente
├── card_job_detail.html       ← verificar con datos reales
├── card_job_list.html         ✅
├── card_job_approval.html     ← revisar
├── card_job_approval_success.html
├── portal_create_user.html    ← mejorar
└── fragments/
    ├── job_table.html         ✅
    ├── color_list.html        ✅
    └── pantone_search_results.html ✅

quotes/tests/
├── conftest.py        ✅ tenant context + RLS
├── factories.py       ✅ PortalUser, StaffUser, CardJobOrder
└── test_portal_security.py  ✅ 15/15 passing
```
