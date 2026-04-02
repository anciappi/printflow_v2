# PrintFlow v2 — Log General de Sesiones

Resumen de alto nivel por sesión. Una línea por módulo tocado.
Para detalle completo ver log-[modulo].md correspondiente.

---

## 2026-03-07
- quotes: diseño portal_login, portal, quote_form — estética High-Tech
- quotes: nuevo modelo CardJobOrder + UI completa card_job_form/detail/list
- core: PortalMiddleware — acceso no autenticado a /portal/login/

## 2026-03-08
- quotes: rebuild card_job_detail.html desde mockup

## 2026-03-16
- tenants: Multi-tenant Phase 1 — django-tenants instalado, schemas separados
- tenants: Branch model movido a tenants app
- tenants: Grupo Velton creado (Velton + Magtik branches)
- core: settings.py SHARED_APPS/TENANT_APPS, TenantMainMiddleware
- inventory: import_stock management command — 4846 unidades Magtik
- security: RLS identificado como necesario — pendiente implementación

## 2026-03-17 (mañana)
- users: RLS implementado — tenant FK en User, TenantContextMiddleware
- users: 9/9 RLS tests pasando
- templates: URLs españolas normalizadas a inglés (8 templates)
- frontend: hex colors reemplazados con tokens semánticos (33 templates)

## 2026-03-17 (tarde)
- users: 9/9 RLS tests — conftest, fixtures, CREATEDB
- templates: URL normalization completada
- frontend: Tailwind tokens en tailwind.config.js, inline config en base.html

## 2026-03-18 (mañana)
- frontend: Tailwind CDN → CLI v4 migración completa
- frontend: input.css con @theme tokens, output.css compilado
- frontend: base.html — CDN removido, link a output.css

## 2026-03-18 (tarde)
- frontend: CDN removido de 6 templates standalone
- frontend: JS inline extraído a 7 archivos en static/js/
- frontend: sidebar.js creado con HTMX state preservation

## 2026-03-19
- inventory: HTMX migración completa — modales, confirmaciones, fragments
- purchasing: HTMX migración completa
- frontend: portal.css unificado para templates standalone
- frontend: hx-boost evaluado y descartado deliberadamente

## 2026-03-20
- quotes: CardJob Sprint 1 — PantoneColor (373 colores), CardJobColor, CardJobFile
- quotes: CardJobOrder extendido — approval_token, quantity, unit_price, delivery
- quotes: STATUS_CHOICES expandido a 8 estados
- quotes: CardJob Sprint 2 — 5 vistas de transición de estados
- quotes: URL pública /aprobar/<uuid>/ implementada
- quotes: card_job_list.html con filtros HTMX y 8 badges de estado
- security: PortalMiddleware simplificado — PORTAL vs STAFF
- security: portal_user FK en CardJobOrder — ownership robusto
- security: PortalCreateUserView — staff crea acceso portal
- security: 15/15 tests de seguridad portal pasando
- frontend: card_job_approval.html, card_job_approval_success.html creados
- frontend: portal_create_user.html creado

## 2026-03-21
- quotes: PantoneSearchView, CardJobColorAddView, CardJobColorRemoveView
- quotes: card_job_form.html rebuild intent (pendiente — UI rota)
- core: superadmin bypass en PortalMiddleware
- infra: planificación restructuración equipo de agentes

## 2026-03-22
- infra: restructuración completa del equipo de agentes
- infra: nueva estructura de logs por módulo
- infra: SKILL-alex.md, skills actualizados
- infra: ARCHITECTURE.md creado

## 2026-03-29
- orders: HTMX status transitions, stage-display model logic, status_badge fragment.
- orders: 7-step production progress bar in workorder_detail.
- frontend: global dark-theme checkbox accent-color fix in main.css.
- orders: stock integration — manual substrate deduction from OT detail (DRY: reutiliza ConsumptionLog).
- orders: stock_panel fragment HTMX + WorkOrderConsumoView. Gated to PRODUCTION+.
- orders: polish — scroll table, HX-Trigger statusUpdated, WorkOrderStockPanelView, DRY helpers.

## 2026-03-30
- orders: listado UI separation — Órdenes activas vs entregadas, histórico en acordeón, extracción DRY `workorder_row.html` fragment.
- orders: panel stock — forzado inline de scrollbox tras 10 items (max-height 350px).

## 2026-04-01
- products: fix loop en submit `product_form.html` — banner global de errores, guard `form.instance.pk` en previews de archivos, `required=False` + `clean()` para campos condicionales deshabilitados por JS, removed `status` duplicado, HTML huérfanos removidos.
- orders: filtro por estado en tablero de OTs — pills dinámicos en `workorder_list.html`, `get_queryset()` filtra por `?status=`, `get_context_data()` pasa choices y filtro activo al contexto.
