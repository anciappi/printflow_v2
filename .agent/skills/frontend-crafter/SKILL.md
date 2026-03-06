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

### Responsive Design
Always build mobile-first:
```html
{# Mobile first, then scale up #}
<div class="w-full md:w-1/2 lg:w-1/3">
```

### Component Consistency
Use these Tailwind patterns consistently across the app:

```html
{# Primary button #}
<button class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
  Action
</button>

{# Danger button #}
<button class="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
  Delete
</button>

{# Card container #}
<div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
  ...
</div>

{# Table #}
<div class="overflow-x-auto rounded-xl border border-gray-200">
  <table class="min-w-full divide-y divide-gray-200">
    <thead class="bg-gray-50">
      <tr>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Column
        </th>
      </tr>
    </thead>
  </table>
</div>

{# Alert / notification #}
<div class="bg-green-50 border border-green-200 text-green-800 rounded-lg p-4">
  Success message
</div>
```

## Behavior Rules
- Never touch `views.py`, `models.py` or any Python file
- If a template change requires backend logic, flag it for BackendArchitect
- Always check that `{% csrf_token %}` is present before submitting any form work
