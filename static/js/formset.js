document.addEventListener('DOMContentLoaded', function() {
    const itemsContainer = document.getElementById('items-container');
    const addButton = document.getElementById('add-item');
    const totalFormsInput = document.getElementById('id_items-TOTAL_FORMS');
    const emptyTemplate = document.getElementById('empty-form-template').innerHTML;

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
    // Auto-rellenar cantidad estándar (MTS/UNI) basado en el material guardado
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
});
