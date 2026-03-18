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
});
