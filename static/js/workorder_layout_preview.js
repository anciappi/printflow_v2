document.addEventListener('DOMContentLoaded', function () {
    const layoutFields = [
        'id_product', 'id_quantity', 'id_layout_rows', 'id_layout_cols',
        'id_gap_horizontal_mm', 'id_gap_vertical_mm', 'id_margin_lateral_mm',
        'id_margin_top_mm', 'id_margin_bottom_mm', 'id_orientation', 'id_bobina_width_mm'
    ];

    const previewContainer = document.getElementById('material-preview-container');
    if (!previewContainer) return;

    function buildPreviewUrl() {
        // Obtenemos la base de la URL inyectada, con fallback al atributo hx-get
        const previewUrlBase = window.layoutPreviewUrl || previewContainer.getAttribute('hx-get');
        if (!previewUrlBase) return "";

        const params = new URLSearchParams();
        layoutFields.forEach(function (id) {
            const el = document.getElementById(id);
            if (el && el.value) params.append(id.replace('id_', ''), el.value);
        });
        return previewUrlBase + "?" + params.toString();
    }

    function refreshPreview() {
        const url = buildPreviewUrl();
        if (!url) return;
        htmx.ajax('GET', url, { target: '#material-preview-container', swap: 'innerHTML' });
    }

    // Debounce helper
    let debounceTimer;
    function debounced() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(refreshPreview, 500);
    }

    layoutFields.forEach(function (id) {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', debounced);
            el.addEventListener('change', debounced);
        }
    });

    // Initial load if product already selected
    const productEl = document.getElementById('id_product');
    if (productEl && productEl.value) {
        refreshPreview();
    }
});
