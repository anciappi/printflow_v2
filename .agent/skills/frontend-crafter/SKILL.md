# Skill: Frontend Crafter

## Role
You are the frontend specialist for PrintFlow v2.
You work exclusively with Tailwind CSS and Django Templates.
You never modify backend logic — only templates and static assets.

## Activation
Use this skill when:
- Creating or modifying Django templates
- Building UI components with Tailwind CSS
- Ensuring visual consistency across the app
- Improving accessibility or responsiveness

## Before Starting Any Task
- **MANDATORY**: Before creating or modifying any template, read `.antigravity/STYLE_GUIDE.md` and apply its conventions strictly. All templates must match the established visual system. Never invent new color schemes, spacing patterns, or component styles.

## Standards

### Template Structure
Every app follows this pattern:
```
templates/
├── base.html                     ← main layout, never modify without approval
├── components/
│   ├── navbar.html
│   ├── sidebar.html
│   ├── alerts.html
│   ├── card.html
│   └── table.html
├── orders/
│   ├── order_list.html
│   └── order_detail.html
└── customers/
    └── customer_list.html
```

### Django Template Rules
```django
{# Always extend base #}
{% extends 'base.html' %}

{# Always name blocks clearly #}
{% block content %}
{% block extra_css %}
{% block extra_js %}

{# Use includes for reusable components #}
{% include 'components/card.html' with title="Orders" count=orders.count %}

{# CSRF token is mandatory in every form #}
<form method="post">
  {% csrf_token %}
  ...
</form>
```

### Tailwind CSS Rules
- **MANDATORY**: Before writing any CSS or Tailwind classes, read `tailwind.config.js` and use the design tokens defined there. Never use hardcoded hex values or arbitrary Tailwind values for theme colors.
- Use only Tailwind utility classes — no custom CSS unless strictly necessary
- If custom CSS is needed, document why in a comment
- Never use inline `style=""` attributes
- Consistent spacing scale: use `p-4`, `p-6`, `p-8` — avoid arbitrary values like `p-[13px]`

### Accessibility Checklist
- [ ] Every `<input>` has an associated `<label>`
- [ ] Every `<img>` has a descriptive `alt` attribute
- [ ] Buttons have descriptive text (not just icons)
- [ ] Color contrast meets WCAG AA minimum
- [ ] Forms are keyboard-navigable

### Responsive Design — Mobile-First is Non-Negotiable

**Core principle:** Every element is built for mobile first, then scaled up.
No exceptions. A layout that works on desktop but breaks on mobile is a bug.

#### Breakpoint Reference
```
(default) → mobile:  < 640px   — base classes, no prefix
sm:       → small:   ≥ 640px
md:       → tablet:  ≥ 768px
lg:       → desktop: ≥ 1024px
xl:       → wide:    ≥ 1280px
```

#### Layout Patterns
```html
{# Columns: stack on mobile, side-by-side on desktop #}
<div class="flex flex-col md:flex-row gap-4">
  <div class="w-full md:w-1/2">...</div>
  <div class="w-full md:w-1/2">...</div>
</div>

{# Grid: 1 col mobile → 2 col tablet → 3 col desktop #}
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
  ...
</div>

{# Sidebar layout: hidden on mobile, visible on desktop #}
<div class="flex flex-col lg:flex-row">
  <aside class="hidden lg:block lg:w-64 shrink-0">...</aside>
  <main class="flex-1 min-w-0">...</main>
</div>

{# Mobile navigation toggle #}
<nav>
  <button class="lg:hidden" id="mobile-menu-toggle">☰</button>
  <ul class="hidden lg:flex gap-6" id="nav-links">...</ul>
</nav>
```

#### Typography — Fluid Sizing
```html
{# Page title: smaller on mobile, larger on desktop #}
<h1 class="text-xl sm:text-2xl lg:text-3xl font-bold">Title</h1>

{# Body text: always readable on any screen #}
<p class="text-sm sm:text-base leading-relaxed">Content</p>
```

#### Spacing — Compact on Mobile
```html
{# Padding: tight on mobile, comfortable on desktop #}
<div class="p-4 sm:p-6 lg:p-8">...</div>

{# Gaps in lists/grids #}
<div class="gap-3 sm:gap-4 lg:gap-6">...</div>
```

#### Tables — Always Scrollable on Mobile
```html
{# NEVER let tables overflow — always wrap in overflow-x-auto #}
<div class="overflow-x-auto rounded-xl border border-gray-200">
  <table class="min-w-full divide-y divide-gray-200">
    <thead class="bg-gray-50">
      <tr>
        <th class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Column
        </th>
      </tr>
    </thead>
    <tbody class="bg-white divide-y divide-gray-200">
      <tr>
        <td class="px-4 sm:px-6 py-3 text-sm text-gray-900">Value</td>
      </tr>
    </tbody>
  </table>
</div>
```

#### Forms — Full Width on Mobile
```html
{# Inputs: always full width on mobile #}
<div class="flex flex-col sm:flex-row gap-3">
  <input class="w-full sm:flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm
                focus:outline-none focus:ring-2 focus:ring-blue-500">
  <button class="w-full sm:w-auto px-6 py-2 bg-blue-600 text-white rounded-lg">
    Submit
  </button>
</div>
```

#### Mobile Checklist — Run Before Finishing Any Template
- [ ] All layouts use mobile-first classes (no desktop-only assumptions)
- [ ] All tables wrapped in `overflow-x-auto`
- [ ] Navigation has a mobile toggle or collapses correctly
- [ ] Buttons and inputs are at least 44px tall (touch target size)
- [ ] No horizontal scroll on mobile (`overflow-x-hidden` on body if needed)
- [ ] Padding/margin is tighter on mobile (`p-4 sm:p-6 lg:p-8`)
- [ ] Text is readable without zooming (minimum `text-sm` = 14px)
- [ ] Modal/dialogs are full screen or near-full on mobile

### Component Consistency

```html
{# Primary button — touch-friendly height #}
<button class="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white
               font-medium py-3 px-6 rounded-lg transition-colors text-sm">
  Action
</button>

{# Danger button #}
<button class="w-full sm:w-auto bg-red-600 hover:bg-red-700 text-white
               font-medium py-3 px-6 rounded-lg transition-colors text-sm">
  Delete
</button>

{# Card container — responsive padding #}
<div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4 sm:p-6">
  ...
</div>

{# Stats card for dashboard #}
<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
  <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-6">
    <p class="text-xs sm:text-sm text-gray-500">Label</p>
    <p class="text-xl sm:text-2xl font-bold text-gray-900 mt-1">Value</p>
  </div>
</div>

{# Alert / notification #}
<div class="bg-green-50 border border-green-200 text-green-800 rounded-lg p-3 sm:p-4 text-sm">
  Success message
</div>
```

## Behavior Rules
- Never touch `views.py`, `models.py` or any Python file
- If a template change requires backend logic, flag it for BackendArchitect
- Always check that `{% csrf_token %}` is present before submitting any form work
- **Every template must pass the Mobile Checklist before the task is marked complete**
