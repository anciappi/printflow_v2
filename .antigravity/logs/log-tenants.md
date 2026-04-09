# PrintFlow v2 — Log: Tenants

## 2026-03-16 — Multi-tenant Phase 1
- django-tenants instalado, schemas separados por cliente
- Branch model movido a `tenants` app
- Grupo Velton creado con branches: Velton + Magtik
- `SHARED_APPS` / `TENANT_APPS` configurados en settings.py
- `TenantMainMiddleware` — subdomain → tenant routing

## 2026-04-09 — Segundo tenant + Auditoría de Aislamiento

### Nuevo tenant: Salleo SRL
- Agregado a `reset_app.sh` (paso 9 y 10)
- schema: `salleo` / domain: `salleo.localhost`
- Branch: Salleo SRL
- Usuario: `salleo_admin` (ADMIN role)
- `runserver.sh` actualizado con URL de Salleo

### Auditoría de aislamiento multi-tenant
Disparada por el descubrimiento de que al crear una OC, el campo `branch` mostraba sucursales de Salleo en la sesión de Velton.

**Vulnerabilidades encontradas y corregidas:**

| Módulo | Archivo | Problema | Fix |
|--------|---------|---------|-----|
| purchasing | `forms.py` | `Branch.objects.all()` en PurchaseOrderForm | Filtro por `get_tenant(request)` |
| purchasing | `views.py` | Sin StaffMixin, sin `request=request` al form | StaffMixin + request pasado |
| orders | `forms.py` | `Branch.objects.all()` en WorkOrderForm | Filtro por `get_tenant(request)` |
| orders | `views.py` | `Branch.objects.all()` en contexto de lista | `filter(tenant=self.request.tenant)` |
| orders | `views.py` | Sin StaffMixin en List/Create/Update/Detail | StaffMixin aplicado |
| orders | `views.py` | Sin `request` al form en Create/Update | `get_form_kwargs()` implementado |
| quotes | `views.py` | `Branch.objects.all()` en CardJobOrderListView | `filter(tenant=self.request.tenant)` |
| inventory | `forms.py` | `PurchaseOrderForm` duplicado con branch sin filtro | Form eliminado |
| inventory | `views.py` | Imports de form obsoleto + sin request al form | Imports corregidos + request pasado |

### Patrón canónico para Branch en forms
```python
def __init__(self, *args, **kwargs):
    request = kwargs.pop('request', None)
    super().__init__(*args, **kwargs)
    if request is not None:
        current_tenant = get_tenant(request)
        self.fields['branch'].queryset = Branch.objects.filter(
            tenant=current_tenant, is_active=True
        )
```

### Patrón canónico para Branch en CBV context
```python
context['branches'] = Branch.objects.filter(
    tenant=self.request.tenant, is_active=True
)
```

### Estado
```
tenants  ✅ multi-tenant operativo — Grupo Velton + Salleo SRL
         ✅ aislamiento de Branch corregido en todos los módulos
```
