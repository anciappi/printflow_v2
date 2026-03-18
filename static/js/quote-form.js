const sameAsBillingCheckbox = document.getElementById('id_same_as_billing');
const deliveryFields = document.getElementById('delivery-fields');

function toggleDelivery() {
    if (sameAsBillingCheckbox.checked) {
        deliveryFields.style.opacity = '0.3';
        deliveryFields.style.pointerEvents = 'none';
        deliveryFields.style.filter = 'grayscale(1)';
    } else {
        deliveryFields.style.opacity = '1';
        deliveryFields.style.pointerEvents = 'auto';
        deliveryFields.style.filter = 'none';
    }
}

// In the original template, the id is usually obtained via {{ form.same_as_billing.id_for_label }}.
// Since it's generic Django, it is primarily "id_same_as_billing" for quotes form.
if (sameAsBillingCheckbox) {
    sameAsBillingCheckbox.addEventListener('change', toggleDelivery);
    window.addEventListener('load', toggleDelivery);
}

// Styling inputs
document.querySelectorAll('input:not([type="checkbox"]):not([type="file"]), select, textarea').forEach(el => {
    el.classList.add('w-full');
});
