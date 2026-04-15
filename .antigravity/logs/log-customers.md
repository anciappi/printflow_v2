# Log: customers — PrintFlow v2

Módulo de gestión de clientes (CRM básico), asignación comercial y vinculación con productos/OTs.

---

## 2026-04-04 | Ficha de Cliente Premium & Asignación Comercial | ✅

**Archivos modificados:** `customers/views.py`, `customers/urls.py`, `templates/customers/customer_detail.html`, `templates/customers/customer_list.html`, `customers/forms.py`, `templates/customers/customer_form.html`

- **CustomerDetailView (Hub Centralizado)**: Implementación de la vista de detalle de cliente con estética "Dark Industrial".
  - **KPIs**: Conteo dinámico de total de productos y órdenes (activas + históricas).
  - **Vinculación de Productos**: Lista de todos los productos asociados al cliente con botón de acceso directo para "Crear OT" desde la ficha.
  - **Seguimiento de Producción**: Sección dedicada a "Órdenes en Curso" (estados PENDING a READY) para visibilidad inmediata del estado de cuenta.
  - **Historial Colapsable**: Acordeón HTMX/Tailwind para órdenes finalizadas (DELIVERED/CANCELLED), manteniendo la interfaz limpia.
- **Asignación Comercial**:
  - Incorporación del campo `assigned_to` (Vendedor) en el modelo y formulario de cliente.
  - Refuerzo de la trazabilidad comercial: cada cliente tiene ahora un responsable directo del equipo de ventas.
- **UX Refinements**:
  - Enlace "Ver cliente" desde el listado general (ícono ojo esmeralda).
  - Normalización de estilos de tablas y badges para consistencia con el resto del sistema.

## 2026-04-06 | Typography & Quick Actions | ✅
- **Quick Links**: Adición del botón "Ver Ficha" en la card de productos asociados para navegación directa a la ficha técnica.
- **Typography Overhaul**: Estandarización a Encode Sans / font-light en el dashboard de clientes y listados de OTs vinculadas.
- **Mono-Removal**: Limpieza de fuentes monospace en CUITs y datos de contacto para mayor elegancia visual.

## 2026-04-12 | Modernización "Dark Industrial" & Búsqueda HTMX | ✅
- **Flat UI Refactor**: Eliminación de acordeones agrupados en favor de una lista plana de alta densidad para mayor rapidez de acceso.
- **HTMX Real-Time Search**: Implementación de búsqueda asíncrona por Nombre o CUIT en `customer_list.html`.
  - Integración de fragmentos (`customer_table.html`) para actualizaciones parciales del DOM.
- **Layout Consistency**: Estructura de 6 columnas (**Razón Social**, **CUIT**, **Email**, **Teléfono**, **Estado**, **Acciones**) con anchos optimizados y tipografía de alta densidad.
- **Actions & Styling**: Unificación de botones de acción tipo badge (`Ver`, `Editar`) en lugar de iconos, alineado con el estándar del Dashboard.

