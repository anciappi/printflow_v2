/**
 * sidebar.js
 * Handles sidebar menu toggle, active state detection,
 * and HTMX swap state preservation for expandable rows.
 */

// ─── SIDEBAR MENU ─────────────────────────────────────────────────────────────

/**
 * Toggles a sidebar submenu open or closed.
 * @param {string} menuId - The ID of the submenu element
 * @param {string} arrowId - The ID of the arrow indicator element
 */
function toggleMenu(menuId, arrowId) {
    const menu = document.getElementById(menuId);
    const arrow = document.getElementById(arrowId);
    if (!menu || !arrow) return;

    if (menu.classList.contains('hidden')) {
        menu.classList.remove('hidden');
        arrow.classList.remove('-rotate-90');
    } else {
        menu.classList.add('hidden');
        arrow.classList.add('-rotate-90');
    }
}

/**
 * Opens the sidebar submenu that matches the current URL path.
 * Runs on initial page load and after every HTMX navigation.
 */
function activateSidebarByPath() {
    const path = window.location.pathname;
    const menuMap = [
        { match: '/inventory/',               menuId: 'menu-inventory',  arrowId: 'arrow-inv' },
        { match: '/customers/',               menuId: 'menu-sales',      arrowId: 'arrow-ven' },
        { match: '/sales/',                   menuId: 'menu-sales',      arrowId: 'arrow-ven' },
        { match: '/purchasing/',              menuId: 'menu-purchasing',  arrowId: 'arrow-comp' },
        { match: '/orders/',                  menuId: 'menu-orders',     arrowId: 'arrow-ord' },
        { match: '/products/',                menuId: 'menu-orders',     arrowId: 'arrow-ord' },
    ];

    menuMap.forEach(({ match, menuId, arrowId }) => {
        const menu = document.getElementById(menuId);
        const arrow = document.getElementById(arrowId);
        if (!menu || !arrow) return;

        if (path.includes(match)) {
            menu.classList.remove('hidden');
            arrow.classList.remove('-rotate-90');
        }
    });
}

// ─── HTMX TOGGLE STATE PRESERVATION ──────────────────────────────────────────

/**
 * Before HTMX swaps content, saves the IDs of all currently expanded rows.
 * Stores them in a data attribute on the target element.
 */
document.addEventListener('htmx:beforeSwap', function (event) {
    const target = event.detail.target;
    if (!target) return;

    const expandedRows = Array.from(target.querySelectorAll('tr[id^="row-"]:not(.hidden)'))
        .map(row => row.id);

    if (expandedRows.length > 0) {
        target.dataset.expandedRows = JSON.stringify(expandedRows);
    }
});

/**
 * After HTMX swaps content, restores previously expanded rows.
 * Reads from the data attribute saved before the swap.
 */
document.addEventListener('htmx:afterSwap', function (event) {
    const target = event.detail.target;
    if (!target || !target.dataset.expandedRows) return;

    const expandedRows = JSON.parse(target.dataset.expandedRows);
    expandedRows.forEach(rowId => {
        const row = document.getElementById(rowId);
        const iconId = rowId.replace('row-', 'icon-');
        const icon = document.getElementById(iconId);
        if (row) {
            row.classList.remove('hidden');
            if (icon) icon.innerText = '-';
        }
    });

    delete target.dataset.expandedRows;

    // Re-activate sidebar after navigation swap
    activateSidebarByPath();
});

// ─── INIT ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', activateSidebarByPath);
