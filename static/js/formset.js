document.addEventListener('DOMContentLoaded', function() {

    // -----------------------------------------------------------------------
    // 1. OC FORMSET — Agregar / eliminar filas de ítems (solo en oc_create)
    // -----------------------------------------------------------------------
    const itemsContainer = document.getElementById('items-container');
    const addButton = document.getElementById('add-item');
    const totalFormsInput = document.getElementById('id_items-TOTAL_FORMS');
    const emptyFormTemplate = document.getElementById('empty-form-template');

    if (itemsContainer && addButton && totalFormsInput && emptyFormTemplate) {
        const emptyTemplate = emptyFormTemplate.innerHTML;

        addButton.addEventListener('click', function() {
            let formIdx = parseInt(totalFormsInput.value);
            let newRowHtml = emptyTemplate.replace(/__prefix__/g, formIdx);
            let tempDiv = document.createElement('div');
            tempDiv.innerHTML = newRowHtml;
            itemsContainer.appendChild(tempDiv.firstElementChild);
            totalFormsInput.value = formIdx + 1;
        });

        itemsContainer.addEventListener('click', function(e) {
            const btn = e.target.closest('.delete-row');
            if (!btn) return;
            const row = btn.closest('.item-row');
            const deleteCheckbox = row.querySelector('input[type="checkbox"][name$="-DELETE"]');

            if (deleteCheckbox) {
                deleteCheckbox.checked = true;
                row.style.display = 'none';
            } else {
                row.remove();
            }
        });
    }

    // -----------------------------------------------------------------------
    // 2. OC FORM — Auto-rellenar MTS/UNI al seleccionar material
    // -----------------------------------------------------------------------
    const materialsDataEl = document.getElementById('materials-data');
    if (materialsDataEl) {
        const materialsData = JSON.parse(materialsDataEl.textContent);

        document.addEventListener('change', function(e) {
            if (e.target.tagName === 'SELECT' && e.target.name.endsWith('-material')) {
                const materialId = e.target.value;
                const prefix = e.target.name.replace('-material', '');
                const qtyInput = document.querySelector(`input[name="${prefix}-quantity_per_unit"]`);

                if (qtyInput && materialId && materialsData[materialId] !== undefined) {
                    qtyInput.value = materialsData[materialId];
                }
            }
        });
    }

    // -----------------------------------------------------------------------
    // 3. CUSTOMER FORM — Toggle dirección de entrega vs. fiscal
    // -----------------------------------------------------------------------
    const deliveryCheckbox = document.getElementById('id_delivery_same_as_fiscal');
    const deliveryBlock = document.getElementById('delivery-address-block');
    const deliverySameMsg = document.getElementById('delivery-same-msg');

    if (deliveryCheckbox && deliveryBlock && deliverySameMsg) {
        function toggleDeliveryBlock() {
            if (deliveryCheckbox.checked) {
                deliveryBlock.classList.add('hidden');
                deliverySameMsg.classList.remove('hidden');
            } else {
                deliveryBlock.classList.remove('hidden');
                deliverySameMsg.classList.add('hidden');
            }
        }

        // Estado inicial al cargar la página
        toggleDeliveryBlock();

        // Escuchar cambios en el checkbox
        deliveryCheckbox.addEventListener('change', toggleDeliveryBlock);
    }

});
