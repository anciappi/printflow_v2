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
