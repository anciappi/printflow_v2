// Zoom Modal Logic — product_detail.js

function openZoomModal(src) {
    const modal = document.getElementById('zoomModal');
    const img = document.getElementById('zoomModalImg');
    img.src = src;
    modal.classList.remove('hidden');
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
    }, 200);
}

document.addEventListener('keydown', (e) => {
    const modal = document.getElementById('zoomModal');
    if (e.key === 'Escape' && modal && !modal.classList.contains('hidden')) {
        closeZoomModal();
    }
});
