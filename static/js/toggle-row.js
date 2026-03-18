function toggleRow(rowId, iconId) {
    const row = document.getElementById(rowId);
    const icon = document.getElementById(iconId);
    if (row.classList.contains('hidden')) {
        row.classList.remove('hidden');
        icon.innerText = '-';
        icon.classList.add('text-slate-400');
    } else {
        row.classList.add('hidden');
        icon.innerText = '+';
        icon.classList.remove('text-slate-400');
    }
}
