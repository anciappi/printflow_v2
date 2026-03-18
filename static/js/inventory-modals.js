function openFraccionarModal(id, name, width) {
    document.getElementById('fracUnitName').innerText = name;
    document.getElementById('fracUnitWidth').innerText = width;
    document.getElementById('fraccionarForm').action = `/inventory/fraccionar/${id}/`;
    document.getElementById('fraccionarModal').classList.remove('hidden');
}

function closeFraccionarModal() {
    document.getElementById('fraccionarModal').classList.add('hidden');
}

function openModal(id, name, maxQty) {
    document.getElementById('modalUnitName').innerText = name;
    document.getElementById('modalMaxQty').innerText = maxQty;
    document.getElementById('consumptionForm').action = `/inventory/consumo/${id}/`;
    document.getElementById('consumptionModal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('consumptionModal').classList.add('hidden');
}
