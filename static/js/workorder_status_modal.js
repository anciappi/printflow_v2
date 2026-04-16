/**
 * workorder_status_modal.js
 * Manages the Work Order status-advance modal.
 *
 * Responsibilities:
 *   1. Defines the global `closeModal()` used by template onclick handlers.
 *   2. Auto-calculates estimated material (meters) when the operator
 *      types the printed quantity during the PRODUCTION → FINISHING transition.
 *
 * Data contract (injected by status_update_modal.html via data-* attributes
 * on the wrapper div #id_qty_produced):
 *
 *   data-layout-rows     → WorkOrder.layout_rows
 *   data-layout-cols     → WorkOrder.layout_cols
 *   data-gap-v           → WorkOrder.gap_vertical_mm
 *   data-margin-top      → WorkOrder.margin_top_mm
 *   data-margin-bottom   → WorkOrder.margin_bottom_mm
 *   data-product-length  → product.height_mm (PORTRAIT) or product.width_mm (LANDSCAPE)
 *   data-waste-pct       → WorkOrder.waste_percentage (%)
 *
 * Formula (mirrors WorkOrder.calculate_material() in models.py):
 *   largo_postura = (rows × productLen) + ((rows − 1) × gapV) + marginTop + marginBottom  [mm]
 *   bocas         = rows × cols
 *   pasadas       = ceil(quantity / bocas)
 *   meters        = (pasadas × largo_postura) / 1000  [× (1 + waste/100) if waste > 0]
 */

// ---------------------------------------------------------------------------
// 1. Global closeModal — called by onclick in the HTMX-injected fragment.
// ---------------------------------------------------------------------------
function closeModal() {
    const modal = document.getElementById('status-update-modal');
    if (modal) modal.remove();
}

// ---------------------------------------------------------------------------
// 2. Material auto-calculator
// ---------------------------------------------------------------------------

/**
 * Reads layout params from the data-* wrapper div, then wires up a live
 * calculation that pre-fills #id_material_used whenever the operator
 * changes the quantity_produced input.
 *
 * The field remains fully editable — the calculated value is only a suggestion.
 */
function initMaterialCalculator() {
    // The wrapper div carries both the data-* params and contains the real input.
    const wrapper = document.getElementById('id_qty_produced');
    if (!wrapper) return;

    // The actual Django-rendered input lives inside the wrapper.
    const qtyInput = wrapper.querySelector('input[name="quantity_produced"]');
    if (!qtyInput) return;

    // Wire all material_used inputs in the modal (one per form section).
    const materialInputs = wrapper.querySelectorAll('input[name="material_used"]');

    // Parse layout parameters from data attributes.
    const rows       = parseFloat(wrapper.dataset.layoutRows)   || 0;
    const cols       = parseFloat(wrapper.dataset.layoutCols)   || 0;
    const gapV       = parseFloat(wrapper.dataset.gapV)         || 0;
    const marginTop  = parseFloat(wrapper.dataset.marginTop)    || 0;
    const marginBot  = parseFloat(wrapper.dataset.marginBottom) || 0;
    const productLen = parseFloat(wrapper.dataset.productLength)|| 0; // mm
    const wastePct   = parseFloat(wrapper.dataset.wastePct)     || 0; // %

    // Without essential geometry we cannot calculate — skip silently.
    if (!rows || !cols || !productLen) return;

    const bocas        = rows * cols;
    // largo_postura in mm
    const largoPostura = (rows * productLen) + ((rows - 1) * gapV) + marginTop + marginBot;

    function recalculate() {
        const qty = parseInt(qtyInput.value, 10);

        if (!qty || qty <= 0) {
            materialInputs.forEach(function (inp) { inp.value = ''; });
            return;
        }

        const pasadas = Math.ceil(qty / bocas);
        // NOTE: NO waste factor — quantity entered already incorporates it.
        const meters = Math.round((pasadas * largoPostura) / 1000);

        // Pre-fill all material inputs with the same rounded value.
        materialInputs.forEach(function (inp) { inp.value = meters; });
    }

    qtyInput.addEventListener('input', recalculate);
    qtyInput.addEventListener('change', recalculate);

    // Fire once in case the field already has a value (e.g., browser autofill).
    if (qtyInput.value) recalculate();
}

// ---------------------------------------------------------------------------
// 3. Bootstrap — runs every time HTMX injects content into #modal-container.
// ---------------------------------------------------------------------------
document.addEventListener('htmx:afterSwap', function (event) {
    if (event.detail.target && event.detail.target.id === 'modal-container') {
        initMaterialCalculator();
    }
});
