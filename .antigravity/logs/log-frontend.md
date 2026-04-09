# Log: frontend — PrintFlow v2

Seguimiento de cambios globales de UI/UX, Tailwind tokens, CSS y fragments transversales.

---

## 2026-03-29 | Orders UI Enhancements | ✅
- **Atomic Fragments**: Creación de `templates/orders/fragments/status_badge.html` siguiendo el patrón de diseño industrial.
- **Production Progress Bar**: Implementación de barra de progreso de 7 pasos en el detalle de la OT.
- **Dark Theme CSS**:
  - `static/css/main.css`: Fix global para checkboxes (`accent-color: #f97316`) para mejor visibilidad en temas oscuros.
- **UX**: Navegación fluida en el cambio de estados sin recarga de página usando HTMX.

## 2026-04-06 | Modernización Tipográfica Global | ✅
- **Encode Sans**: Migración total a la fuente Encode Sans, eliminando fuentes serif/sans genéricas y monospace.
- **Normal/Light Design**: Estandarización de pesos tipográficos. Se prohibió el uso de `font-bold` y `font-semibold`, reemplazándolos por `font-normal` (400) y `font-light` (300).
- **Industrial Hierarchy**: Mejoras en la legibilidad mediante el uso de `tracking-widest`, `uppercase` y contrastes tonales en lugar de grosor de fuente.
- **Login UI**: Rediseño de la pantalla de acceso para alinearla con la estética premium VS Code del resto del sistema.

## 2026-04-08 | Dashboard Hub Operativo | ✅
- **Premium Layout**: Implementación de `dashboard/index.html` con grid asimétrico y KPIs horizontales.
- **Fixed Semantic Classes**: Hardcoding de clases de estado (`text-blue-400`, etc.) para asegurar compatibilidad con el motor de purga de Tailwind v4 en modo CLI.
- **UX**: Navegación rápida desde sidebar y redirección inteligente desde la raíz.
- **Inline KPI Cards**: Diseño de alto impacto visual con íconos vectoriales y tipografía Encode Sans Light.

