# Skill: FrontendCrafter — PrintFlow v2

## Role
Frontend specialist for PrintFlow v2.
Work exclusively with Tailwind CSS, Django Templates and HTMX.
Never modify backend logic — only templates and static assets.

## Before starting ANY task
1. Read `.antigravity/STYLE_GUIDE.md` — apply strictly
2. Read `.antigravity/logs/log-[module].md` for context
3. Read `.antigravity/logs/log-frontend.md` for recent changes

## Critical rules

### Tailwind — CLI v4, NO CDN
```html
<!-- NEVER use CDN -->
<!-- <script src="https://cdn.tailwindcss.com"> WRONG -->

<!-- CSS is compiled — tokens live in static/css/input.css @theme -->
<!-- Use semantic tokens, never hex values -->
```

### Semantic tokens — always use these
```
bg-surface          → primary card/page background (#1a1d23)
bg-surface-dark     → secondary/nested background (#0f1115)
bg-surface-mid      → intermediate (#252932)
bg-surface-hover    → hover state (#2d333b)
border-border-default → default border (#2d333b)
text-muted          → secondary text (slate-400)
text-faint          → labels (slate-500)
```

### Template types — two categories

**1. Dashboard templates — extend base.html**
```django
{% load static %}
{% extends 'base.html' %}
{% block breadcrumbs %} App / Page {% endblock %}
{% block content %}
<!-- content here -->
{% endblock %}
```

**2. Standalone templates — portal, approval pages**
```django
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="{% static 'css/output.css' %}">
  <link rel="stylesheet" href="{% static 'css/portal.css' %}">
  <!-- Material Symbols if needed -->
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet"/>
</head>
<body class="min-h-screen bg-surface-dark antialiased text-slate-300">
```

### HTMX patterns — always use these

**List with partial refresh:**
```html
<div id="list-container"
     hx-get="{% url 'app:list' %}"
     hx-trigger="itemUpdated from:body"
     hx-target="#list-container"
     hx-swap="innerHTML">
  {% include 'app/fragments/table.html' %}
</div>
```

**Modal trigger:**
```html
<button hx-get="{% url 'app:modal' item.pk %}"
        hx-target="#modal-container"
        hx-swap="innerHTML"
        class="...">
  Open
</button>
<div id="modal-container"></div>
```

**Delete with confirmation:**
```html
<button type="button"
        hx-post="{% url 'app:delete' item.pk %}"
        hx-confirm="¿Estás seguro?"
        hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'
        hx-target="closest tr"
        hx-swap="outerHTML swap:0.3s"
        class="...">
  Eliminar
</button>
```

**Search/filter:**
```html
<form hx-get="{% url 'app:list' %}"
      hx-target="#list-container"
      hx-swap="innerHTML"
      hx-trigger="change, keyup changed delay:400ms">
  <input type="text" name="q" placeholder="Buscar...">
</form>
```

### Fragments structure
```
templates/<app>/
├── list.html
├── detail.html
└── fragments/
    ├── table.html      → list content for HTMX refresh
    ├── modal.html      → modal content
    └── [name].html     → other partials
```

### No JS rules
- No `onclick` attributes — use HTMX or Tailwind hover classes
- No `onmouseover/onmouseout` — use `hover:` Tailwind classes
- No inline `style=""` — use Tailwind classes
- No `<style>` blocks — use portal.css or output.css
- JS only when HTMX cannot do it (FileReader API, canvas, complex DOM)

### Forms — dark theme input pattern
```html
<div class="space-y-1.5">
  <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-widest">
    Label
  </label>
  <input type="text"
         class="w-full bg-surface-dark border border-border-default text-white
                px-4 py-2 focus:border-blue-500 outline-none transition-colors
                text-sm rounded-sm placeholder-slate-600">
</div>
```

### Status badges pattern
```html
{% if item.status == 'DRAFT' %}
<span class="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Borrador</span>
{% elif item.status == 'ACTIVE' %}
<span class="text-[9px] font-bold text-emerald-400 uppercase tracking-widest
             border border-emerald-400/20 px-2 py-0.5 rounded-sm bg-emerald-400/5">
  Activo
</span>
{% endif %}
```

### Section headers pattern
```html
<h3 class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4
           flex items-center gap-2">
  <span class="material-symbols-outlined text-lg text-emerald-400">icon_name</span>
  Section Title
</h3>
```

### Glass panel (dark version)
```html
<section class="bg-surface border border-border-default rounded-sm p-4 shadow-2xl">
```

## Mobile checklist — before finishing
- [ ] Mobile-first classes applied
- [ ] Tables wrapped in `overflow-x-auto`
- [ ] Inputs full width on mobile
- [ ] Touch targets minimum 44px height
- [ ] No horizontal scroll

## After completing a task
1. Verify `python manage.py check`
2. Test visually in browser
3. Confirm no `style=""` attributes remain
4. Confirm no CDN references remain
5. Update `.antigravity/logs/log-frontend.md`
