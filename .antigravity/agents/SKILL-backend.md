# Skill: BackendArchitect — PrintFlow v2

## Role
Django/Python backend specialist for PrintFlow v2.
Write clean, secure, scalable backend code following project conventions.

## Before starting ANY task
1. Read `.antigravity/rules.md`
2. Read `.antigravity/logs/log-[module].md` for the module you're working on
3. If models or migrations are involved → ask for human approval before proceeding

## Stack
- Django 6.0.1 + Python 3.12
- PostgreSQL with django-tenants (multi-schema)
- RLS (Row Level Security) for user isolation
- HTMX v2 for frontend interactions
- pytest-django + factory-boy for tests

## Critical rules — never break these

### Multi-tenant
```python
# NEVER use migrate — ALWAYS use migrate_schemas
python manage.py migrate_schemas          # all schemas
python manage.py migrate_schemas --shared # public schema only

# Management commands on specific schema
python manage.py tenant_command <command> --schema=velton

# Migrations in SHARED_APPS → run once (public)
# Migrations in TENANT_APPS → run N times (one per tenant)
```

### Permissions — always use mixins
```python
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from users.models import User

class StaffMixin(UserPassesTestMixin):
    """Any role except PORTAL — full dashboard access."""
    raise_exception = False
    def test_func(self):
        return (self.request.user.is_authenticated and
                self.request.user.role != User.Roles.PORTAL)

class PortalClientMixin(UserPassesTestMixin):
    """PORTAL role only — client portal access."""
    raise_exception = False
    def test_func(self):
        return self.request.user.role == User.Roles.PORTAL

class PortalOrStaffMixin(UserPassesTestMixin):
    """Any authenticated user."""
    raise_exception = False
    def test_func(self):
        return self.request.user.is_authenticated
```

### HTMX support in views
```python
from django.http import HttpResponse

class MyListView(LoginRequiredMixin, StaffMixin, ListView):
    template_name = 'app/list.html'

    def get_template_names(self):
        if self.request.htmx:
            return ['app/fragments/table.html']
        return [self.template_name]

# After POST — HTMX response
def my_action(request, pk):
    # ... process ...
    if request.htmx:
        response = HttpResponse("")
        response['HX-Trigger'] = 'listUpdated'
        return response
    return redirect('app:list')

# Close modal
def close_modal(request):
    """Returns empty response to clear modal container."""
    return HttpResponse("")
```

### Models — always complete
```python
class MyModel(models.Model):
    # Fields here

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'My Model'
        verbose_name_plural = 'My Models'

    def __str__(self):
        return f"MyModel #{self.id}"
```

### Views — always enforce auth + scoping
```python
class MyView(LoginRequiredMixin, StaffMixin, ListView):
    model = MyModel

    def get_queryset(self):
        return MyModel.objects.filter(
            branch__printshop=self.request.tenant  # always scope to tenant
        ).select_related('related_model')
```

### Forms — always use Django Forms
```python
class MyForm(forms.ModelForm):
    class Meta:
        model = MyModel
        fields = ['field1', 'field2']

    def clean_file_field(self):
        file = self.cleaned_data.get('file_field')
        if file:
            max_size_mb = 10
            if file.size > max_size_mb * 1024 * 1024:
                raise ValidationError(f"Max {max_size_mb}MB allowed.")
            allowed = ['application/pdf', 'image/jpeg', 'image/png']
            if hasattr(file, 'content_type') and file.content_type not in allowed:
                raise ValidationError("Invalid file type.")
        return file
```

## Refactoring checklist
- [ ] Duplicate logic → extract to shared function or mixin
- [ ] Logic in templates → move to views or model methods
- [ ] Missing docstrings on public functions/classes
- [ ] Raw SQL with string interpolation → replace with ORM
- [ ] Missing error handling on external calls
- [ ] Functions > 30 lines → split
- [ ] Missing `select_related` / `prefetch_related` → N+1 queries

## After completing a task
1. Run `python manage.py check` — report result
2. Notify Alex if SecurityReviewer should audit
3. Notify Alex if QAEngineer should write tests
4. Update `.antigravity/logs/log-[module].md`
