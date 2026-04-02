# Log: products — PrintFlow v2

Seguimiento de cambios en la app Products (Maestro de Productos), modelo de negocio y formularios de carga técnica.

---

## 2026-03-31 | Ficha de Producto: Modernización UI "Dark Industrial" & Gestión de Tintas CMYK | ✅
- **Refactorización UI**: Migración total de `product_form.html` a la estética "Dark Industrial" estructurado en "Cards" de superficie oscura (`bg-surface`).
- **Grillas 50/50 y Compactado**: Se implementó una redistribución visual para el 'Anverso' y 'Reverso'. La imagen de pre-visualización (50%) convive con el bloque de HTMX de tintas (50%) en un layout dinámico. Los campos de texto libre de observaciones se migraron a columnas *Full-Width* en las bases de sus respectivas tarjetas para mejor legibilidad.
- **Seeding Permanente (CMYK)**: Se aseguró la siembra de la base de datos introduciendo y conectando globalmente al final del script destructivo `reset_app.sh` la ejecución automática y obligatoria de `python seed_cmyk.py` garantizando integridad a futuro.
- **Documentación Técnica Limpia**: Transición de inputs de subida HTML standard a una tabla interactiva de descarga y gestión para archivos tipo de Sacabocado y Originales que homogeniza el estándar de la App.
- **Modal Viewers**: Lógica de visores in-situ "Full Screen" con controles de blur back-drop para diseños (frente y dorso).

---

## 2026-04-01 | product_form.html — Corrección de loop en submit + imágenes rotas + validaciones silenciosas | ✅

**Archivos modificados:** `templates/products/product_form.html`, `products/forms.py`

- **Bug principal (loop al guardar):** El formulario re-renderizaba en lugar de redirigir a `products:catalog` por errores de validación que no eran visibles. Se agregó un banner global de errores al top del form (`{% if form.errors %}`) listando todos los campos con problema.
- **Imágenes rotas en CREATE fallido:** Todos los `{% if form.instance.design_front %}` (y análogos para `design_back`, `diecut_file`, `tech_file`) fueron corregidos a `{% if form.instance.pk and form.instance.design_front %}`. Sin este guard, al re-renderizar un CREATE fallido Django intentaba llamar `.url` sobre un archivo no guardado en disco.
- **Campos condicionales obligatorios (`varnish_type`, `laminate_type`, `mag_coercivity`):** El JavaScript desactiva estos selects con `disabled` cuando su toggle principal está en False. Los inputs `disabled` no se envían en el POST → Django los rechazaba como obligatorios. Fix en `forms.py`: `required=False` para los 6 campos de config + método `clean()` que restaura los defaults del modelo (`'NONE'`) cuando el toggle correspondiente está apagado.
- **Campo `status` duplicado:** `{{ form.status }}` se renderizaba dos veces (sección Identificación y sección Medidas). Se eliminó la segunda ocurrencia.
- **Errores de campos requeridos sin feedback:** `qty_per_box`, `width_mm` y `height_mm` no mostraban sus mensajes de error individuales. Se agregaron los bloques `{% if form.X.errors %}`.
- **HTML roto:** Removido `</script>` huérfano y `</div>` huérfano que quedaban al final del template.
