function openReceptionModal(pk, currentRemito, supplierName) {
    // Llenar datos visuales
    document.getElementById('modalSupplierName').innerText = supplierName;

    // Pre-llenar el input con el número de OC actual
    document.getElementById('modalRemitoInput').value = currentRemito;

    // Configurar la URL de envío
    const form = document.getElementById('receptionForm');
    form.action = `/inventory/remitos/recibir/${pk}/`;

    // Mostrar modal
    document.getElementById('receptionModal').classList.remove('hidden');

    // Auto-focus en el input
    setTimeout(() => {
        document.getElementById('modalRemitoInput').select();
    }, 100);
}

function closeReceptionModal() {
    document.getElementById('receptionModal').classList.add('hidden');
}
