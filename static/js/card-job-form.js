// Sync checkboxes with hidden CharFields
function updateColors(side) {
    const checkboxes = document.querySelectorAll(`.color-${side}`);
    const hiddenInput = document.getElementById(`id_${side}_colors`);
    const selected = Array.from(checkboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.getAttribute('data-color'))
        .join(',');
    if (hiddenInput) {
        hiddenInput.value = selected;
    }
}

document.querySelectorAll('.color-front').forEach(cb => {
    cb.addEventListener('change', () => updateColors('front'));
});
document.querySelectorAll('.color-back').forEach(cb => {
    cb.addEventListener('change', () => updateColors('back'));
});

// Styling inputs
document.querySelectorAll('input:not([type="checkbox"]):not([type="file"]), select, textarea').forEach(el => {
    el.classList.add('w-full');
});

// Pre-fill hidden requester info from user if possible (simplified for this demo)
// In a real scenario, this would be handled in form_valid or via template variables
