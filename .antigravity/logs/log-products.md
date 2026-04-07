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

---

## 2026-04-06 | Migración a Múltiples Archivos de Documentación Técnica | ✅

**Archivos modificados:** `products/models.py`, `products/forms.py`, `products/views.py`, `products/urls.py`, `templates/products/product_form.html`, `static/js/product_form.js`

- **Refactorización del Modelo (`ProductDocument`)**: Se eliminaron los campos estáticos `tech_file` y `diecut_file` del modelo `Product`. Se creó el modelo relacional `ProductDocument` con `ForeignKey` a `Product`, permitiendo carga ilimitada de archivos categorizados por `doc_type` (TECH/DIECUT).
- **Trazabilidad (`uploaded_by`)**: Se integró el campo `uploaded_by` vinculado al modelo de usuario de Django para registrar quién realizó cada carga.
- **Gestión Asíncrona HTMX**:
    - Implementación de `ProductDocumentDeleteView` para borrado físico y lógico de archivos sin recargar el formulario.
    - Corrección de error 403 (Forbidden) mediante el uso de `hx-headers` para incluir el token CSRF en peticiones `DELETE`.
    - Uso de `hx-confirm` para validación de borrado en dos etapas solicitada por el usuario.
- **Rediseño UI Premium**:
    - Consolidación a una sola columna en la sección de "Documentación Técnica".
    - Tipografía `font-light` y tamaño `text-xs` para mejorar la elegibilidad de metadatos (fecha, usuario, nombre).
    - Botonera de acción rectificada (`w-8 h-8`) con iconos SVG (Download/Trash) y efectos hover sólidos.
- **Live Preview**: Lógica en `static/js/product_form.js` para mostrar una lista de archivos seleccionados localmente antes de confirmar el guardado de la ficha.

---

## 2026-04-06 | Implementación de ProductDetailView y Hub Técnico | ✅

**Archivos modificados:** `products/views.py`, `products/urls.py`, `templates/products/product_detail.html`, `static/js/product_detail.js`, `templates/products/product_list.html`, `templates/customers/customer_detail.html`

- **Visualización Técnica 360° (`ProductDetailView`)**:
    - Creación de la vista de detalle centralizada modelada bajo el estándar de `customer_detail.html`.
    - Integración de **KPIs de producción**: Listado de OTs activas y acordeón colapsable para historial de entregas/cancelaciones.
    - Segmentación de documentación técnica (Originales vs. Sacabocados) con metadatos de autoría y descarga directa.
- **Diseño Premium "Dark Industrial"**:
    - Galería de diseño (Anverso/Reverso) con **Zoom Modal** dinámico (`product_detail.js`) y efectos de escala.
    - Cuadrícula de especificaciones optimizada: Ancho, Largo/Alto y Sustrato unificados en una sola fila para mayor densidad de información.
    - Visualización de terminaciones mediante **badges semánticos** (Laminados, Barnices, Chips, etc.) con códigos de color específicos.
- **Unificación Tipográfica**: Migración total a **Encode Sans**, eliminando fuentes mono y reduciendo pesos a `font-normal` (400) y `font-light` (300) para una estética "Dark Industrial" premium.
- **Ecosistema de Navegación**:
    - Inclusión de botones "Ver Ficha" en el catálogo general y en el detalle de cliente.
    - Vinculación directa para creación de nuevas OTs pre-cargando el producto seleccionado.

