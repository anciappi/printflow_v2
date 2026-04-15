# Log: inventory — PrintFlow v2

Módulo de gestión de stock, materiales, depósitos y trazabilidad de consumos.

---

## 2026-04-06 | Dashboard Optimization & Typography | ✅
- **Inventory Dashboard**: Rediseño completo de la tabla de stock en `inventory/dashboard.html` bajo el nuevo estándar visual.
- **Typography Overhaul**: Migración a **Encode Sans** y remoción de `font-mono` en medidas (cm) y gramajes (g).
- **Stock Indicators**: Refactor de píldoras de "Bajo Stock" y alertas de faltantes usando pesos `font-normal` para mayor elegancia.
- **Layout Consistency**: Ajuste de anclajes y espaciado en la tabla de disponibilidad para soportar fuentes con menor peso visual.

---

## 2026-04-09 | Arquitectura Multi-Material & UI Segmentada | ✅
- **Refactor Core (`inventory/models.py`)**: Migración de esquema monolítico enfocado en "Bobinas" a un sistema genérico capaz de modelar múltiples sustratos mediante el nuevo modelo dinámico `MaterialCategory` y el soporte transaccional para unidades abstractas (Kg, Lts, Unidades y Hojas).
- **Formularios Adaptables**: Ampliación física en `MaterialForm` integrando métricas de empaque (`sheets_per_package`, `stack_height_cm`) y unidades matriciales.
- **Dashboard Multi-Categoría (`inventory_table.html`)**: Refactor visual implementando `{% regroup %}` para desfragmentar la visualización del stock base. Cada conjunto activo rinde su tabla aislada e independiente para evitar cruces dispares (Mts. vs Lts.).
- **Flujo de Fraccionamiento**: Restringido algorítmicamente mediante el atributo `allows_fractioning` originado de las categorías.
- **Estado UI HTMX Automático**: Inserción de listener JavaScript transversal en `purchaseorder_list.html` sensible a eventos `ocUpdated`, induciendo validación en vivo y autorecarga de pendientes sin fricción.

---

## 2026-04-10 | Fraccionamiento Longitudinal & Bug Fix Crítico | ✅
- **Multi-Fraccionamiento por Largo**: Implementación del método `fraccionar_por_largo` en `InventoryUnit`. Permite generar múltiples bobinas hijas simultáneas desde un solo input (ej: "1000, 500"), calculando el remanente automáticamente.
- **Fix: Bug de Stock Fantasma**: Reescritura del método `deshacer_fraccionamiento`. Ahora el sistema detecta si la restauración es de ancho o largo, sumando las cantidades iniciales de las hijas para reconstruir el disponible exacto de la madre, eliminando la duplicación de stock en bobinas consumidas.
- **UI Modal Rediseño**: Refactor integral de `fraccionar_modal.html` a un sistema de doble pestaña (Ancho | Largo) con JavaScript nativo.
- **JS Extraction**: Extracción de lógica del modal a `static/js/fraccionar_modal.js` siguiendo las reglas de arquitectura de "no hardcoded scripts".

## 2026-04-12 | Alta Densidad en Dashboard | ✅
- **Refactor de Fila Única**: Rediseño del listado de stock en `dashboard.html` para unificar Categoría, Nombre, Cantidad y Medidas en una sola línea.
- **Micro-Tipografía Tech**: Aplicación de `text-[10px]` y fuentes light para maximizar la densidad de información sin comprometer la legibilidad.
- **Anchos Optimizados**: Ajuste manual de `max-w` por columna para evitar espacios muertos y alinear visualmente la tabla con los módulos de Clientes y OTs.
