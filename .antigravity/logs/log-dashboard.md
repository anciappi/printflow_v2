# Log: dashboard — PrintFlow v2

Módulo de visualización centralizada (Hub Operativo) y métricas en tiempo real.

---

## Sprint: Dashboard Initial Implementation | 2026-04-08 | CERRADO ✅

- **App Architecture**: Creación de la aplicación `dashboard` para desacoplar el panel principal del `core`.
- **View Logic (`DashboardView`)**: 
  - Centralización de datos de `customers`, `inventory` y `orders`.
  - Agregación de `total_stock` por material mediante `Sum` y `Q` filters (solo stock disponible/en uso).
  - Filtrado de `active_orders` (excluyendo DELIVERED/CANCELLED) con `select_related` optimizado.
- **UI "Dark Industrial" Hub**:
  - **KPI Bar**: Rediseño de 3 cards independientes horizontales con íconos, títulos y contadores alineados.
  - **Recent Data Grid**: Paneles para Clientes Recientes y Materiales con Stock Activo.
  - **Work Orders Hub**: Tabla completa de producción vigente con columnas de Estado (colores semánticos) y Prioridad (Rush tags).
- **Security**: Integración de `LoginRequiredMixin` y redirección automática de root `/` a `/dashboard/`.
- **Tailwind v4 Fix**: Hardcoding de clases semánticas para estados de OT (`text-blue-400`, `bg-emerald-500`, etc.) para evitar purgas del CLI en build-time durante el escaneo de templates.

## Sprint: Dashboard Purchasing Update | 2026-04-08 | CERRADO ✅

- **View Logic**: Integración de compras pendientes en la vista a través del `purchasing.PurchaseOrder.objects.filter(status='PENDING')` limitando a los 5 más recientes.
- **UI Extension**: Ampliación del Grid principal principal (`grid-cols-2` a `lg:grid-cols-3`) para incluir una nueva tarjeta compacta de "Ingresos Pendientes", respetando el estilo de Dark Industrial con iconos y listados rápidos optimizados para lectura.
- **UI Optimization**: Redistribución jerárquica moviendo la grilla full-width de "Órdenes Vigentes" a la franja superior directa bajo los KPIs. Reducción global del 'padding' en todas las celdas de las tablas (`px-5` -> `px-4`, `py-2.5` -> `py-1.5`) para incrementar la densidad de datos mostrados en el monitor sin comprometer la legibilidad.

