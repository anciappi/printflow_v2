# PrintFlow v2 — Style Guide

This document defines the visual language and Tailwind CSS patterns used in the PrintFlow v2 project, based on established templates like `inventory_list.html` and `portal_login.html`.

## 1. Color Palette

The project uses a dark, "High-Tech" corporate aesthetic.

### Backgrounds
- **Primary Page/Card:** `bg-[#1a1d23]` (Slate-Dark)
- **Secondary/Nested:** `bg-[#0f1115]`
- **Row Hover:** `hover:bg-[#2d333b]/30`
- **Modal Overlay:** `bg-black/70 backdrop-blur-sm`

### Borders
- **Default Border:** `border-[#2d333b]`
- **Subtle/Lighter:** `border-slate-800`
- **Accent/Focus:** `focus:border-blue-500`, `focus:border-red-500`

### Semantic Colors
- **Text Primary:** `text-white`
- **Text Secondary/Muted:** `text-slate-400`, `text-slate-500`
- **Status Success:** `text-emerald-400`, `text-emerald-500`
- **Status Warning/Active:** `text-amber-500`
- **Action/Link:** `text-blue-400`, `text-blue-500`
- **Special/Highlight:** `text-purple-400`

---

## 2. Typography

### Regla General: Dark Industrial Font Weights
> **Bold** → `font-normal` | **Regular/Medium** → `font-light`
> El objetivo es reducir el ruido visual y lograr un look técnico y premium.

### Headings
- **Main Titles (OT number, page title):** `text-xl font-normal text-white tracking-tight`
- **Section Headers:** `text-xs font-light text-slate-400 uppercase tracking-widest`
- **Subtitles/Descriptions:** `text-[10px] font-light text-slate-500 uppercase tracking-[0.2em]`

### Data & Tables
- **Table Headers (`th`):** `text-[9px] font-light text-slate-500 uppercase tracking-widest`
- **Data values (primary):** `text-sm font-light text-white`
- **Data values (accent):** `text-sm font-normal text-orange-400` or `text-blue-400`
- **Micro-labels:** `text-[9px] text-slate-500 uppercase tracking-widest`
- **Monospaced data (IDs, dates):** `font-mono text-blue-300 text-[10px]`
- **Material Consumption (ml/m):** Always round to the nearest integer (`|floatformat:0`) for readability, as centimeters are not relevant in production charts.

### Form Labels
- `text-[10px] font-light text-slate-500 uppercase tracking-widest`

### Buttons
- **Primary (CTA):** `font-normal`
- **Secondary/Ghost:** `font-light`

---

## 3. Table Structure

Tables follow a structured, high-density layout.

### Wrapper
```html
<div class="bg-[#1a1d23] border border-[#2d333b] overflow-hidden rounded-sm shadow-2xl">
    <table class="w-full text-left border-collapse">
        ...
    </table>
</div>
```

### Rows & Cells
- **Header Cell (`th`):** `px-4 py-2 border-b border-[#2d333b] bg-[#0f1115]/50`
- **Body Cell (`td`):** `px-4 py-2`
- **Row Polish:** `divide-y divide-[#2d333b]` applied to `tbody`.

---

### Action (In-Table/Small)
`bg-[#2d333b] px-2 py-0.5 rounded text-[10px] font-light transition-colors`
- **Modifier (Danger):** `hover:text-red-400`
- **Modifier (Action):** `hover:text-amber-500`

### Main (Modal/Form)
`text-xs font-normal uppercase px-4 py-2 rounded-sm transition-all`
- **Primary Action (Confirm):** `bg-orange-600 text-white hover:bg-orange-500`
- **Danger Action:** `bg-red-600 text-white hover:bg-red-700`
- **Secondary (Cancel):** `text-slate-500 font-light hover:text-white`

---

## 5. Modal Structure

Modals are centered with a blurred overlay.

```html
<div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="fixed inset-0 bg-black/70 backdrop-blur-sm"></div>
    <div class="relative z-10 bg-[#1a1d23] border border-[#2d333b] w-full max-w-lg p-6 shadow-2xl">
        <!-- Content -->
    </div>
</div>
```

---

## 6. Form Inputs

Inputs should be consistent and high-contrast.

```html
<label class="block text-[10px] font-bold text-slate-500 uppercase mb-2">Label</label>
<input type="text" class="w-full bg-[#0f1115] border border-[#2d333b] text-white px-4 py-2 focus:border-blue-500 outline-none transition-colors">
```

---

## 7. Badges & Indicators

### Status Badge (Pills)
`bg-[#2d333b] text-slate-300 text-[12px] px-2 py-0.5 rounded-full border border-slate-600`

### Inline Icon Indicators
- **Available:** `text-[9px] text-emerald-500` (e.g., `✔ Disp.`)
- **Warning:** `text-[9px] text-amber-500` (e.g., `⚠ En Uso`)

---

## 8. Spacing & Layout

- **Page Container:** `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`
- **Section Spacing:** `mb-4` or `space-y-4`
- **Grid Patterns:** `grid grid-cols-1 md:grid-cols-2 gap-4`
