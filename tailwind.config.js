/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        // ─── BACKGROUNDS ──────────────────────────────
        'surface':        '#1a1d23', // Primary card/page background
        'surface-dark':   '#0f1115', // Secondary/nested background  
        'surface-mid':    '#252932', // Intermediate — merge #21262d, #16181d here
        'surface-hover':  '#2d333b', // Row hover / interactive state

        // ─── BORDERS ──────────────────────────────────
        'border-default': '#2d333b', // Default border
        'border-subtle':  '#1e2530', // Subtle/lighter border

        // ─── TEXT ─────────────────────────────────────
        'text-muted':     '#94a3b8', // slate-400 — secondary text
        'text-faint':     '#64748b', // slate-500 — faint/labels

        // ─── SEMANTIC ─────────────────────────────────
        'success':        '#10b981', // emerald-500
        'warning':        '#f59e0b', // amber-500
        'danger':         '#ef4444', // red-500
        'info':           '#3b82f6', // blue-500
        'special':        '#a855f7', // purple-400
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        'sm': '2px',   // Buttons, badges — sharp corporate feel
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
