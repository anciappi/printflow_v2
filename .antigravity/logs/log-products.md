# Log: products — PrintFlow v2

Seguimiento de cambios en la app Products (Maestro de Productos), modelo de negocio y formularios de carga técnica.

---

## 2026-03-31 | Ficha de Producto: Modernización UI "Dark Industrial" & Gestión de Tintas CMYK | ✅
- **Refactorización UI**: Migración total de `product_form.html` a la estética "Dark Industrial" estructurado en "Cards" de superficie oscura (`bg-surface`).
- **Grillas 50/50 y Compactado**: Se implementó una redistribución visual para el 'Anverso' y 'Reverso'. La imagen de pre-visualización (50%) convive con el bloque de HTMX de tintas (50%) en un layout dinámico. Los campos de texto libre de observaciones se migraron a columnas *Full-Width* en las bases de sus respectivas tarjetas para mejor legibilidad.
- **Seeding Permanente (CMYK)**: Se aseguró la siembra de la base de datos introduciendo y conectando globalmente al final del script destructivo `reset_app.sh` la ejecución automática y obligatoria de `python seed_cmyk.py` garantizando integridad a futuro.
- **Documentación Técnica Limpia**: Transición de inputs de subida HTML standard a una tabla interactiva de descarga y gestión para archivos tipo de Sacabocado y Originales que homogeniza el estándar de la App.
- **Modal Viewers**: Lógica de visores in-situ "Full Screen" con controles de blur back-drop para diseños (frente y dorso).
