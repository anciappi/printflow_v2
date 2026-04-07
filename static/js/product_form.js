function addColorRow(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const fieldName = containerId.includes('front') ? 'colors_front' : 'colors_back';
    const hiddenSelect = document.querySelector(`select[name="${fieldName}"]`);
    if (!hiddenSelect) return;
    const optionsHtml = Array.from(hiddenSelect.options).map(opt =>
        `<option value="${opt.value}">${opt.text}</option>`
    ).join('');
    const rowId = 'color-row-' + Math.random().toString(36).substr(2, 9);
    const row = document.createElement('div');
    row.id = rowId;
    row.className = 'flex items-center gap-2 px-3 py-1.5 bg-[#0f1115] border border-[#2d333b] rounded-md shadow-sm';
    row.innerHTML = `
        <span class="w-3.5 h-3.5 rounded-full bg-slate-700 border border-slate-600 shrink-0"></span>
        <select class="dynamic-color-select flex-1 bg-[#0f1115] border-none text-slate-400 text-xs focus:ring-0 cursor-pointer outline-none m-0 p-0" onchange="syncColors('${fieldName}')">
            <option value="">Seleccionar tinta...</option>
            ${optionsHtml}
        </select>
        <button type="button" onclick="removeColorRow('${rowId}', '${fieldName}')" class="text-slate-600 hover:text-red-500 transition-colors ml-auto shrink-0 p-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
    `;
    container.appendChild(row);
}

function removeColorRow(rowId, fieldName) {
    const row = document.getElementById(rowId);
    if (row) row.remove();
    syncColors(fieldName);
}

function syncColors(fieldName) {
    const containerId = fieldName.replace('_', '-') + '-container';
    const container = document.getElementById(containerId);
    const hiddenSelect = document.querySelector(`select[name="${fieldName}"]`);
    if (!container || !hiddenSelect) return;
    const selects = container.querySelectorAll('.dynamic-color-select');
    Array.from(hiddenSelect.options).forEach(opt => opt.selected = false);
    selects.forEach(s => {
        if (s.value) {
            const opt = Array.from(hiddenSelect.options).find(o => o.value === s.value);
            if (opt) opt.selected = true;
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const defaultColors = ['Cyan', 'Magenta', 'Amarillo', 'Negro'];
    ['colors_front', 'colors_back'].forEach(fieldName => {
        const hiddenSelect = document.querySelector(`select[name="${fieldName}"]`);
        if (!hiddenSelect) return;
        const containerId = fieldName.replace('_', '-') + '-container';
        const container = document.getElementById(containerId);
        if (!container) return;
        const selectedOptions = Array.from(hiddenSelect.options).filter(opt => opt.selected);
        if (selectedOptions.length > 0) {
            selectedOptions.forEach(opt => {
                addColorRow(containerId);
                const lastSelect = container.lastElementChild.querySelector('select');
                if (lastSelect) { lastSelect.value = opt.value; syncColors(fieldName); }
            });
        } else {
            let defaultsAdded = 0;
            defaultColors.forEach(colorName => {
                const opt = Array.from(hiddenSelect.options).find(o => o.text.trim().toLowerCase() === colorName.toLowerCase());
                if (opt) { addColorRow(containerId); const lastSelect = container.lastElementChild.querySelector('select'); if (lastSelect) { lastSelect.value = opt.value; defaultsAdded++; } }
            });
            if (defaultsAdded > 0) { syncColors(fieldName); } else { addColorRow(containerId); }
        }
    });

    handleFileStatus('id_design_front', 'status-design_front', 'preview-design_front');
    handleFileStatus('id_design_back', 'status-design_back', 'preview-design_back');
    handleFileStatus('id_diecut_file', 'status-diecut_file');
    handleFileStatus('id_tech_file', 'status-tech_file');

    // Lógica para Especificaciones Técnicas (Desactivar/Activar por fila)
    const specRows = document.querySelectorAll('.spec-row');
    specRows.forEach(row => {
        const mainToggleInput = row.querySelector('.spec-main-toggle input[type="checkbox"]');
        if (!mainToggleInput) return;
        
        const relatedInputs = row.querySelectorAll('.spec-front input, .spec-back input, .spec-config select, .spec-config input');
        
        const updateState = () => {
            const isChecked = mainToggleInput.checked;
            relatedInputs.forEach(input => {
                if (!isChecked && input.type === 'checkbox') input.checked = false;
                input.disabled = !isChecked;
                if (input.disabled) {
                    input.classList.add('opacity-30', 'cursor-not-allowed');
                } else {
                    input.classList.remove('opacity-30', 'cursor-not-allowed');
                }
            });
            
            const dependentRows = document.querySelectorAll(`.dependent-row[data-depends-on="${mainToggleInput.id}"]`);
            dependentRows.forEach(depRow => {
                const depInputs = depRow.querySelectorAll('input, select');
                depInputs.forEach(input => {
                    input.disabled = !isChecked;
                    if (input.disabled) {
                        input.classList.add('opacity-30', 'cursor-not-allowed');
                    } else {
                        input.classList.remove('opacity-30', 'cursor-not-allowed');
                    }
                });
                if (!isChecked) depRow.classList.add('opacity-40', 'pointer-events-none');
                else depRow.classList.remove('opacity-40', 'pointer-events-none');
            });
        };

        mainToggleInput.addEventListener('change', updateState);
        updateState();
    });
});

function handleFileStatus(inputId, statusId, previewId = null) {
    const input = document.getElementById(inputId);
    const status = document.getElementById(statusId);
    if (!input || !status) return;
    input.addEventListener('change', function () {
        const file = this.files[0];
        if (file) {
            const fieldName = inputId.replace('id_', '');
            const clearCheckbox = document.getElementById(`${fieldName}-clear_id`);
            if (clearCheckbox) clearCheckbox.checked = false;
            status.innerHTML = `<span class="dot"></span> NUEVO: ${file.name.substring(0, 15)}...`;
            status.className = 'status-badge status-badge-nuevo';
            if (previewId) {
                const preview = document.getElementById(previewId);
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = e => { 
                        preview.innerHTML = `
                        <div class="group relative w-full h-full cursor-pointer overflow-hidden rounded-[7px] bg-surface-dark" onclick="openZoomModal('${e.target.result}')">
                            <img src="${e.target.result}" class="w-full h-full object-contain transition-transform duration-300 group-hover:scale-[1.03]">
                            <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-[1px]">
                                <svg class="w-8 h-8 text-white drop-shadow-md" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"/></svg>
                            </div>
                        </div>`; 
                    };
                    reader.readAsDataURL(file);
                } else {
                    preview.innerHTML = `<div class="text-center p-4"><svg class="w-8 h-8 text-slate-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg><span class="text-[9px] text-slate-500 font-bold uppercase">${file.name.split('.').pop()}</span></div>`;
                }
            }
        }
    });
}

function markForDeletion(fieldName) {
    const clearCheckbox = document.getElementById(`${fieldName}-clear_id`);
    const status = document.getElementById(`status-${fieldName}`);
    const preview = document.getElementById(`preview-${fieldName}`);
    const input = document.getElementById(`id_${fieldName}`);
    if (clearCheckbox) {
        clearCheckbox.checked = true;
        if (input) input.value = '';
        if (status) { status.innerHTML = `<span class="dot"></span> Marcado para eliminar`; status.className = 'status-badge status-badge-eliminado'; }
        if (preview) { preview.innerHTML = `<div class="text-center p-4 opacity-30"><svg class="w-8 h-8 text-red-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg></div>`; }
    }
}

// Modal Zoom Logic
function openZoomModal(src) {
    const modal = document.getElementById('zoomModal');
    const img = document.getElementById('zoomModalImg');
    img.src = src;
    modal.classList.remove('hidden');
    // Animation frame trick for smooth entry
    requestAnimationFrame(() => {
        img.classList.remove('scale-95', 'opacity-0');
        img.classList.add('scale-100', 'opacity-100');
    });
}

function closeZoomModal() {
    const modal = document.getElementById('zoomModal');
    const img = document.getElementById('zoomModalImg');
    if (!modal || !img) return;
    img.classList.remove('scale-100', 'opacity-100');
    img.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
        modal.classList.add('hidden');
        img.src = '';
    }, 200); // match transition duration
}

document.addEventListener('keydown', (e) => {
    const modal = document.getElementById('zoomModal');
    if (e.key === 'Escape' && modal && !modal.classList.contains('hidden')) {
        closeZoomModal();
    }
});

// File Preview Logic for Multiple Files
function updateFilePreview(inputElement, previewListId) {
    const list = document.getElementById(previewListId);
    if (!list) return;
    list.innerHTML = ''; 
    if (inputElement.files && inputElement.files.length > 0) {
        list.innerHTML = `<li class="text-blue-400 font-bold mb-1 list-none">Archivos listos para adjuntar (Guardar para confirmar):</li>`;
        Array.from(inputElement.files).forEach(file => {
            const li = document.createElement('li');
            li.className = 'text-slate-300 text-xs ml-4';
            li.textContent = file.name;
            list.appendChild(li);
        });
    }
}
