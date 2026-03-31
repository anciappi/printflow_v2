# Log: orders — PrintFlow v2

Módulo responsable de gestión de órdenes de trabajo (OT), seguimiento de producción y estados.

---

## Sprint: Orders Sprint 2 - Status HTMX | 2026-03-29 | CERRADO ✅
- **Status Transitions**: Implementación de lógica de estados industrial (PENDING → ... → DELIVERED).
- **WorkOrderStatusUpdateView**: Vista basada en `View` para procesar cambios de estado vía HTMX POST.
- **Model Logic**: Método `WorkOrder.get_next_status_display()` para controlar el flujo desde el modelo.
- **HTMX Integration**: 
  - `orders/fragments/status_badge.html`: Fragmento para actualización atómica del bloque de estado.
  - Uso de `hx-target="#status-block"` y `hx-swap="outerHTML"`.
- **Query Optimization**: `select_related` en `WorkOrderDetailView` para evitar queries N+1.

## Sprint: Orders Sprint 3 - Stock Integration | 2026-03-29 | CERRADO ✅
- **DRY**: Reutiliza `ConsumptionLog` de inventory — sin modelos nuevos, sin migraciones.
- **WorkOrderConsumoView**: Vista HTMX POST que crea `ConsumptionLog` con `reference_ot=order.ot_number`.
- **Gating**: Descuento habilitado solo desde estado `PRODUCTION` en adelante.
- **WorkOrderDetailView**: Contexto enriquecido con `stock_units`, `stock_total`, `consumos_ot`, `can_consume`.
- **Fragment**: `orders/fragments/stock_panel.html` — panel HTMX swappable con:
  - Info del sustrato del producto.
  - Tabla de unidades disponibles con colores según nivel de stock.
  - Formulario de descuento (visible solo si `can_consume`).
  - Historial de consumos registrados para esta OT.
  - Alerta naranja si no hay stock del material.
- **Pendiente sprint futuro**: Tintas, polímeros e insumos varios. FK formal de `ConsumptionLog → WorkOrder`.

## Sprint: Orders Sprint 3b - Polish | 2026-03-29 | CERRADO ✅
- **Orden Mágico Natural**: Las unidades de inventario mostradas en la tabla de OTs ahora implementan el algoritmo de "Ordenamiento Natural", procesando los números y letras de la unidad por separado para ordenar correlativamente correctamtente (1, 2, 3 ... 10 en lugar de 1, 10, 11).
- **Sticky header e internal scroll**: Reestructuración de la tabla `stock_panel` para encapsular toda la tabla en un container con `overflow-y-auto` y height máximo, pero manteniendo el `<thead class="sticky top-0">` para el scroll correcto.
- **DRY refactor**: `_build_stock_context()` + `_render_stock_panel()` como helpers de módulo — sin duplicación entre views.
- **`WorkOrderStockPanelView`**: Nuevo GET endpoint para re-fetch HTMX del panel de stock.
- **Auto-refresco al avanzar estado**: `WorkOrderStatusUpdateView` emite `HX-Trigger: statusUpdated`. El `stock_panel` escucha `statusUpdated from:body` y se auto-refetchía — el formulario de descuento aparece solo al entrar a PRODUCTION sin recargar la página.

## Sprint: Orders Sprint 3c - UI Refinements | 2026-03-30 | CERRADO ✅
- **Listado UI**: Anotación por `is_delivered` en `WorkOrderListView` para separar visualmente activas de finalizadas.
- **Histórico Acordeón**: Órdenes terminadas agrupadas bajo un componente desplegable para mantener el foco en la producción en curso.
- **Micro-Fragments DRY**: `orders/fragments/workorder_row.html` creado para reutilizar el HTML de las filas sin repetir código.
- **Stock Panel Polish**: Scroll interno asegurado sin cortar UI limitando inline `max-height: 350px`.

## Archivos del módulo
```
orders/
├── models.py          → WorkOrder (STATUS_CHOICES, get_next_status_display)
├── views.py           → WorkOrderStatusUpdateView, WorkOrderDetailView
├── urls.py            → status_update endpoint
├── forms.py           → WorkOrderForm
└── templates/orders/
    ├── workorder_detail.html    → Status badge + Progress bar
    └── fragments/
        └── status_badge.html    → Fragmento HTMX
```
