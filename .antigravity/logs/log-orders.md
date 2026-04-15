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

## Sprint: Orders Sprint 4 - Filtro por Estado en Tablero | 2026-04-01 | CERRADO ✅
- **`WorkOrderListView.get_queryset()`**: Lee `request.GET.get('status', '')`, valida contra `WorkOrder.STATUS_CHOICES`, y aplica `.filter(current_status=status_filter)` si corresponde.
- **`WorkOrderListView.get_context_data()`**: Pasa `current_status_filter` y `status_choices` al template.
- **`workorder_list.html`**: Barra de pills dinámica generada con `{% for value, label in status_choices %}` — pill activo en naranja (`bg-orange-600`), inactivos en `bg-surface-dark`. Pill "Todos" limpia el filtro. Indicador de filtro activo con link "Limpiar filtro" cuando hay selección.
- **Sin JS**: Filtro puramente via GET params — sin romper paginación ni el acordeón de entregadas.
- **Archivos modificados**: `orders/views.py`, `templates/orders/workorder_list.html`.
## Sprint: Orders Sprint 5 - Dashboard Premium UI & Ficha Médica (HTMX) | 2026-04-01 | CERRADO ✅
- **Filtro Avanzado**: Rediseño integral de estilo industrial ("Filter Bar"). Inclusión de rangos de fecha y sucursales conectadas a la vista con contadores en tiempo real.
- **Ficha Médica (Trazabilidad)**: Creación de un subsistema incrustado para hacer un track log por cada avance u observación operativa.
  - Modelo `WorkOrderLog` incrustado.
  - CRUD con `WorkOrderLogCreateView`, `WorkOrderLogUpdateView` y `WorkOrderLogDeleteView`.
  - Despliegue asíncrono con modalidad de recargas puntuales vía fragmentos HTMX (`log_feed.html`).
- **UI Full Width Re-structure**: Se demolió el formato particionado del detalle de la OT pasando a capas apiladas y horizontales que exprimen el ancho total, al igual que nuestro módulo inventario de OC.
- **Micro-modal CRUD**: Botones explícitos nativos de Editar/Borrar en la grilla que activan modales en-pantalla en la zona designada (`modal-container`) de forma aislada.


## Sprint: Orders Sprint 6 - Material Calculation Module | 2026-04-04 | CERRADO ✅

Hito estratégico: Implementación de la calculadora de consumo de bobina en tiempo real para Órdenes de Trabajo.

**Archivos modificados:** `orders/models.py`, `orders/forms.py`, `orders/views.py`, `orders/urls.py`, `templates/orders/workorder_form.html`, `templates/orders/fragments/material_preview.html`, `templates/orders/fragments/product_details.html`

- **Model Level Logic (Core Engine)**:
  - 8 nuevos campos de postura en `WorkOrder`: `layout_rows`, `layout_cols`, `gap_horizontal_mm`, `gap_vertical_mm`, `margin_lateral_mm`, `margin_top_mm`, `margin_bottom_mm`, `orientation`.
  - Método `calculate_material()`: Fórmula industrial que procesa el largo de avance (Portrait/Landscape), mermas fijas por márgenes y gaps, y pasadas necesarias según cantidad solicitada.
  - Auto-cálculo en `save()`: Persistencia automática de `estimated_material_usage` (metros lineales) y `bocas` totales al guardar la OT.
- **HTMX Real-time Preview**:
  - `LayoutPreviewView`: Endpoint GET de alto rendimiento que devuelve el fragmento calculado.
  - `material_preview.html`: Panel visual interactivo con 4 KPIs (Bocas, Pasadas, Largo Polímero, Metros Est.).
  - **Sistema de Alerta de Ancho**: Campo `bobina_width_mm` (opcional). El preview detecta si el ancho de postura supera el material disponible y dispara una alerta visual roja ("Warning Mode") con instrucciones de ajuste.
- **UX Refinements**:
  - Unificación del flujo: eliminación de botones de creación manual — toda OT nace desde un Producto.
  - Formulario limpio: remoción de campos huérfanos/redundantes (`bocas` manual, `material_used` duplicado).
  - Debounce JS (500ms) para evitar sobrecarga de red durante el tipeo de parámetros de postura.

---

## Archivos del módulo
```
orders/
├── models.py          → WorkOrder (STATUS_CHOICES, calculate_material)
├── views.py           → WorkOrderStatusUpdateView, LayoutPreviewView
├── urls.py            → status_update, layout_preview endpoints
├── forms.py           → WorkOrderForm (layout fields + bobina_width_mm)
└── templates/orders/
    ├── workorder_form.html      → Configuración de Postura + HTMX Preview
    └── fragments/
        ├── status_badge.html    → Fragmento HTMX
        └── material_preview.html → Panel de Estimación

---

## 2026-04-06 | Modernización Tipográfica Global | ✅
- **Encode Sans Integration**: Barrido completo de `workorder_list.html` y `workorder_detail.html` para unificar la tipografía del sistema.
- **Weight Reduccion**: Eliminación de `font-bold` y `font-medium`, estandarizando en `font-normal` (400) y `font-light` (300).
- **Atomic Refactor**: Actualización visual de `workorder_row.html` (fragmento de tabla) para mejorar el aire y la legibilidad en listados densos sin usar negritas.
- **Status Pills**: Ajuste de contrastes en estados de producción para mantener la visibilidad con fuentes más delgadas.

```

## Sprint: Orders Sprint 7 - UI Polish & JS Extraction | 2026-04-07 | CERRADO ✅
- **Ficha Médica (log_feed)**: Estética unificada con el resto del tablero "Dark Industrial" (fondos `#0f1115`, bordes sutiles, hover states consistentes).
- **WorkOrder Detail**: Cabecera simplificada a una tira compacta eliminando paneles huérfanos. Estado "Estado de Producción" compactado a pastilla ("pill") para optimizar espacio vertical.
- **Product Details Preview**: Lógica condicional refinada para que oculte dinámicamente filas vacías/falsas y ocupe menos espacio.
- **WorkOrder Form Layout**: Rediseño a un layout asimétrico balanceado (50/50 CSS Grid) apilando "Cronograma" y "Observaciones" a la derecha, frente a la "Configuración de Postura" a la izquierda. Reparado bug en `product_details.html` que provocaba overflow del contenedor rompiendo la experiencia visual.
- **JS Extraction**: Extracción completa de script on-page para previsualización de material. Movido a `static/js/workorder_layout_preview.js` y refactorizado para tomar la URL base a través de una variable inyectada global en `window`, desacoplando completamente rutas estáticas y añadiendo caché-busting auto-gestionado.

## Sprint: Dashboard Integration | 2026-04-08 | CERRADO ✅
- **Active Orders Queryset**: Implementación de lógica en `DashboardView` para capturar solo órdenes vigentes (excluyendo entregadas/canceladas).
- **Status Semantic UI**: Integración de la tabla de órdenes en el dashboard con mapeo visual de estados y prioridades Rush (rojo/bold) alineado al sistema de diseño.

---

## 2026-04-09 | OTs Hotfix & Customer Onboarding | ✅
- **Alta Rápida de Cliente**: Habilitación nativa de anclaje `+ Crear Cliente` embebido paramétricamente dentro del formulario de Alta de OT (`workorder_form.html`) contiguo a la selección del cliente, resolviendo fricción productiva para comerciales.

- **UI Real-time**: Inclusión del input de demasía en `workorder_form.html` con reactividad instantánea vía `hx-include` y visualización desglosada en el fragmento `material_preview.html`.

## 2026-04-12 | OT Detail Redesign & Stock UX Polish | ✅
- **Layout 60/40**: Rediseño integral de `workorder_detail.html` adoptando el patrón de "Ficha de Cliente". Estructura segmentada en dos columnas para mejorar la densidad de información técnica.
- **Data Split**: Segmentación visual entre "Solicitado por Cliente" y "Cálculo de Planta" para transparencia en el uso de demasía.
- **Logistics Integration**: Inclusión de tarjeta de "Contacto y Envío" con datos directos del cliente (email, tel, dirección de entrega) para agilidad en despacho.
- **Stock Panel UX**: 
  - Historial de consumos movido fuera del acordeón para visibilidad inmediata tras registrar.
  - Inclusión de **ancho de bobina** en el selector de unidades para evitar errores de operario.
  - Normalización tipográfica: eliminación de hashtags (`#`) en nombres de unidades para limpieza visual.
  - Unificación de descripción de sustrato en una sola línea (Nombre / Tipo / Ancho / Gramaje).
- **CSS Hotfix**: Reemplazo de grids de 5 columnas por contenedores `flex` y grids estándar de 2 columnas para compatibilidad con el build actual de Tailwind.

## 2026-04-12 | Modernización de Listado & Alta Densidad | ✅
- **UI Consistency**: Refactorización de `workorder_list.html` bajo el estándar "Dark Industrial".
  - Contenedor ajustado a `max-w-7xl` para alineación global.
  - Header y Breadcrumbs simplificados con enfoque en tipografía técnica.
- **Badge-Style Actions**: Reemplazo de iconos de acción por botones tipo badge (`Ver`, `Editar`) unificando el patrón visual de los listados maestros.
- **Historical Toggle**: Rediseño del botón de "Órdenes Finalizadas" inspirado en el Dashboard, eliminando el estilo previo de acordeón.
- **Urgency Highlights**: Implementación de micro-animación *pulse* en OTs urgentes para visibilidad inmediata.
- **Filter Maintenance**: Preservación de la barra de filtros original (fiel al diseño pre-modernización) por requerimiento de UX técnica.

