function switchTab(tabId) {
    const tipoCorte = document.getElementById('tipo_corte');
    if (!tipoCorte) return;
    
    tipoCorte.value = tabId;
    
    const btnAncho = document.getElementById('tab-btn-ancho');
    const btnLargo = document.getElementById('tab-btn-largo');
    const contentAncho = document.getElementById('tab-content-ancho');
    const contentLargo = document.getElementById('tab-content-largo');
    const inputAncho = document.getElementById('input_ancho');
    const inputLargo = document.getElementById('input_largo');

    if (tabId === 'ancho') {
        btnAncho.className = "flex-1 py-2 text-xs font-bold uppercase transition-colors text-amber-500 border-b-2 border-amber-500";
        btnLargo.className = "flex-1 py-2 text-xs font-bold uppercase transition-colors text-slate-500 hover:text-slate-300";
        contentAncho.classList.remove('hidden');
        contentLargo.classList.add('hidden');
        inputAncho.setAttribute('required', 'required');
        inputLargo.removeAttribute('required');
    } else {
        btnLargo.className = "flex-1 py-2 text-xs font-bold uppercase transition-colors text-amber-500 border-b-2 border-amber-500";
        btnAncho.className = "flex-1 py-2 text-xs font-bold uppercase transition-colors text-slate-500 hover:text-slate-300";
        contentLargo.classList.remove('hidden');
        contentAncho.classList.add('hidden');
        inputLargo.setAttribute('required', 'required');
        inputAncho.removeAttribute('required');
    }
}

function prepareSubmit() {
    const tipoCorte = document.getElementById('tipo_corte');
    if (!tipoCorte) return;
    
    const tab = tipoCorte.value;
    if(tab === 'ancho') {
        document.getElementById('input_largo').value = "";
    } else {
        document.getElementById('input_ancho').value = "";
    }
}

// Configuración inicial basada en la pestaña activa
(function() {
    const tipoCorte = document.getElementById('tipo_corte');
    if (tipoCorte) {
        switchTab(tipoCorte.value);
    }
})();
