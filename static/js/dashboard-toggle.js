function toggleAgotados() {
    const wrapper = document.getElementById('agotados-wrapper');
    const icon = document.getElementById('agotados-icon');
    
    if (wrapper.classList.contains('hidden')) {
        // ABRIR
        wrapper.classList.remove('hidden');
        wrapper.classList.add('animate-fade-in-down');
        icon.style.transform = 'rotate(180deg)';
    } else {
        // CERRAR
        wrapper.classList.add('hidden');
        icon.style.transform = 'rotate(0deg)';
    }
}
