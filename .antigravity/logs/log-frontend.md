# Log: frontend — PrintFlow v2

Seguimiento de cambios globales de UI/UX, Tailwind tokens, CSS y fragments transversales.

---

## 2026-03-29 | Orders UI Enhancements | ✅
- **Atomic Fragments**: Creación de `templates/orders/fragments/status_badge.html` siguiendo el patrón de diseño industrial.
- **Production Progress Bar**: Implementación de barra de progreso de 7 pasos en el detalle de la OT.
- **Dark Theme CSS**:
  - `static/css/main.css`: Fix global para checkboxes (`accent-color: #f97316`) para mejor visibilidad en temas oscuros.
- **UX**: Navegación fluida en el cambio de estados sin recarga de página usando HTMX.
