# PrintFlow v2 — Log: Purchasing

## 2026-04-09 — Security Audit: Tenant Isolation Fix

### Problema identificado
Al crear una nueva Orden de Compra, el campo `branch` (Sucursal Destino) mostraba branches de **todos los tenants** — incluyendo tenants ajenos como Salleo SRL.

### Root cause
`PurchaseOrderForm` no filtraba el queryset de `branch`. Django usaba el default `Branch.objects.all()` que cruza todos los schemas del schema público.

### Fix aplicado

**`purchasing/forms.py`**
- `PurchaseOrderForm.__init__` acepta `request` via `kwargs.pop('request', None)`
- Filtra: `Branch.objects.filter(tenant=get_tenant(request), is_active=True)`

**`purchasing/views.py`**
- `StaffMixin` definido localmente (bloquea rol PORTAL)
- `@login_required + StaffMixin` aplicado a `create_purchase_order` y `edit_purchase_order`
- `request=request` pasado al form en las 4 instanciaciones (GET y POST de create y edit)

**`inventory/views.py`** (módulo legacy de OC que aún existe)
- Imports redirigidos de `inventory.forms` → `purchasing.forms`
- `request=request` pasado al form en `create_purchase_order` y `edit_purchase_order`

### Estado del módulo
```
purchasing  ✅ HTMX completo + tenant isolation corregido
```
