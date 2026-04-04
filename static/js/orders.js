function toggleEntregadas() {
    const wrapper = document.getElementById('entregadas-wrapper');
    const icon = document.getElementById('entregadas-icon');
    
    if (wrapper && icon) {
        if (wrapper.classList.contains('hidden')) {
            wrapper.classList.remove('hidden');
            wrapper.classList.add('animate-fade-in-down');
            icon.style.transform = 'rotate(180deg)';
        } else {
            wrapper.classList.add('hidden');
            wrapper.classList.remove('animate-fade-in-down');
            icon.style.transform = 'rotate(0deg)';
        }
    }
}
