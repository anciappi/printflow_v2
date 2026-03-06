# Audit Report - PrintFlow v2

## core + users ✅ DONE

### App: `core/`
1. ✅ **What is correct**:
   - Environment variables loaded via `python-dotenv`.
   - Custom user model configured (`users.User`).
   - Standard Django middleware and template configurations.
2. ⚠️ **What needs refactoring**:
   - **Insecure Fallbacks**: `SECRET_KEY` and `DB_PASSWORD` have hardcoded defaults/fallbacks in `settings.py`.
   - **URL Consistency**: Inconsistent naming in `urls.py` (mix of English and Spanish).
   - **Example**:
     ```python
     # Before
     SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-...')
     
     # After
     from django.core.exceptions import ImproperlyConfigured
     SECRET_KEY = os.getenv('SECRET_KEY')
     if not SECRET_KEY:
         raise ImproperlyConfigured("SECRET_KEY must be set in .env")
     ```
3. ❌ **Missing for production-readiness**:
   - Security headers (`SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS`).
   - `ALLOWED_HOSTS` configuration for production environments.
   - Custom error handlers (`handler404`, `handler500`).
4. 🔗 **Dependencies**: All other apps depend on `core` for settings and global URL routing.
5. 🔴 **Security issues**:
   - **Critical**: Hardcoded `SECRET_KEY` fallback in `settings.py` (line 27).
   - **Critical**: Hardcoded `DB_PASSWORD` default in `settings.py` (line 99).

---

### App: `users/`
1. ✅ **What is correct**:
   - Extension of `AbstractUser` for custom user model.
   - Use of `TextChoices` for user roles (`ADMIN`, `MANAGEMENT`, `DESIGNER`, `TEAM`, `SALES`).
   - Proper registration in Django Admin with extended `fieldsets`.
2. ⚠️ **What needs refactoring**:
   - **Missing Meta**: Models lack `Meta` class and standard `ordering`.
   - **Missing Timestamps**: User model lacks `created_at` and `updated_at` fields as required by project rules.
   - **Example**:
     ```python
     # Before
     class User(AbstractUser):
         ...
     
     # After
     class User(AbstractUser):
         created_at = models.DateTimeField(auto_now_add=True)
         updated_at = models.DateTimeField(auto_now=True)
         ...
         class Meta:
             ordering = ['-created_at']
     ```
3. ❌ **Missing for production-readiness**:
   - Role-based access control (RBAC) logic in views or managers is not yet defined.
   - Custom user profile management forms/views (currently empty).
4. 🔗 **Dependencies**: Referenced by `core.settings.AUTH_USER_MODEL` and used across the system for authentication.
5. 🔴 **Security issues**:
   - No specific vulnerabilities in the current model structure, but lack of granular permission checks in views remains a risk once features are added.

---

## orders + customers

### App: `orders/`
1. ✅ **What is correct**:
   - Comprehensive model `WorkOrder` with proper choices for status and priority.
   - Use of `Django ModelForms` (`WorkOrderForm`).
   - Views correctly enforce authentication via `LoginRequiredMixin`.
2. ⚠️ **What needs refactoring**:
   - **Missing Timestamps**: Model lacks `updated_at` (required by rules).
   - **Manual ID Generation**: `save()` method manually calculates `ot_number`, which is prone to race conditions under concurrent requests.
   - **Unscoped QuerySets**: List view does not scope by user/permissions, exposing all orders.
   - **Example**:
     ```python
     # Before
     class WorkOrderListView(LoginRequiredMixin, ListView):
         model = WorkOrder
         # get_queryset is missing, defaults to WorkOrder.objects.all()

     # After
     class WorkOrderListView(LoginRequiredMixin, ListView):
         model = WorkOrder
         # ...
         def get_queryset(self):
             return WorkOrder.objects.filter(sales_rep=self.request.user).select_related('customer', 'product')
     ```
3. ❌ **Missing for production-readiness**:
   - Pagination in the `ListView`.
   - Granular permissions (e.g., only allowing status changes by authorized roles).
   - A robust mechanism to generate sequential OT numbers (e.g., database sequence or atomic transaction).
4. 🔗 **Dependencies**: Depends on `users.User` (sales_rep) and `products.Product` (product).
5. 🔴 **Security issues**:
   - **High**: Unscoped querysets in `WorkOrderListView` and `WorkOrderUpdateView` allow any authenticated user to view and modify any order.
   - **Medium**: High risk of race conditions resulting in duplicate `ot_number` values during concurrent creation.

---

### App: `customers/`
1. ✅ **What is correct**:
   - Solid `Customer` model definition, including uniqueness for `tax_id`.
   - Views use `LoginRequiredMixin`.
   - Use of `Django Forms` for creation and updates.
2. ⚠️ **What needs refactoring**:
   - **Missing Timestamps**: Model lacks `updated_at` (required by rules).
   - **View Logic**: Unscoped querysets in `CustomerListView` and `CustomerUpdateView`.
   - **UI in Forms**: Tailwind CSS classes are hardcoded directly into `customers/forms.py`, violating separation of concerns.
   - **Example**:
     ```python
     # Before
     class Customer(models.Model):
         created_at = models.DateTimeField(auto_now_add=True)
         # missing updated_at

     # After
     class Customer(models.Model):
         created_at = models.DateTimeField(auto_now_add=True)
         updated_at = models.DateTimeField(auto_now=True)
     ```
3. ❌ **Missing for production-readiness**:
   - Pagination in `CustomerListView`.
   - Soft-delete functionality. Currently uses standard `DeleteView` which permanently deletes records, violating the "No deletion of existing data" rule without approval/safeguards.
4. 🔗 **Dependencies**: Depends on `core` for authentication/routing.
5. 🔴 **Security issues**:
   - **High**: Unscoped access allows any authenticated user to edit or completely delete any customer via `CustomerDeleteView` and `CustomerUpdateView`.

---

## inventory + products + purchasing

### App: `inventory/`
1. ✅ **What is correct**:
   - Complex stock logic (fractioning units, consumption logs) handled via `transaction.atomic()`.
   - Use of `inlineformset_factory` for purchasing items.
   - Managerial summaries using proxy models.
2. ⚠️ **What needs refactoring**:
   - **Performance**: `InventoryListView` performs Python-side sorting on unit numbers, which will scale poorly.
   - **DRY**: Redundant view logic and forms between `inventory` and `purchasing`.
   - **Form Styling**: Hardcoded Tailwind classes in `forms.py`.
   - **Example**:
     ```python
     # Before (inventory/views.py)
     for mat in context['materiales']:
         mat.active_units.sort(key=natural_sort_key)

     # After
     # Use database-level ordering during Prefetch or custom manager methods
     Prefetch('units', queryset=InventoryUnit.objects.order_by('purchase_order__remito_number', 'unit_number'))
     ```
3. ❌ **Missing for production-readiness**:
   - `updated_at` timestamps on all models and `Meta` classes on several.
   - User-role scoping (who can fraction? who can mark as received?).
4. 🔗 **Dependencies**: `users`, `core`.
5. ⚡ **Performance issues**:
   - `StockDashboardView` recalculates sums/counts across all materials on every hit.
   - Potential N+1 in `mark_as_received` loop if items count is high.

---

### App: `products/`
1. ✅ **What is correct**:
   - Proper model structure with timestamps and soft-delete ready status.
   - Catalog view correctly uses `prefetch_related` for efficiency.
   - Proper use of `limit_choices_to` for data integrity.
2. ⚠️ **What needs refactoring**:
   - **Metadata**: `Color` model lacks timestamps and meta-ordering.
   - **Scoping**: Update/Delete views allow access to any product regardless of relationship.
   - **Example**:
     ```python
     # Before
     class ProductUpdateView(LoginRequiredMixin, UpdateView):
         model = Product

     # After
     class ProductUpdateView(LoginRequiredMixin, UpdateView):
         model = Product
         def get_queryset(self):
             return Product.objects.filter(...) # Define scoping rules
     ```
3. ❌ **Missing for production-readiness**:
   - Pagination in the catalog view.
   - Audit logs for design/file changes.
4. 🔗 **Dependencies**: `customers`, `inventory` (substrate).
5. ⚡ **Performance issues**:
   - The M2M relation for colors (`colors_front`, `colors_back`) needs careful prefetching in detailed views to avoid N+1 queries.

---

### App: `purchasing/`
1. ✅ **What is correct**:
   - Explicit `select_related` and `prefetch_related` in `PurchaseOrderListView`.
   - Atomic creation of orders with UUID-based unique identifiers.
2. ⚠️ **What needs refactoring**:
   - **Massive Duplication**: Almost 90% of views and forms are duplicates of `inventory`. This app should either be merged into `inventory` or exclusively handle the purchasing workflow while `inventory` handles units/consumption.
   - **URL Overlap**: Overlapping paths in `core/urls.py` can cause confusion.
3. ❌ **Missing for production-readiness**:
   - Formal separation from inventory models or migration of those models to this app.
   - Scoping of purchases by sucursal or department.
4. 🔗 **Dependencies**: Reuses `inventory.models` entirely.
5. ⚡ **Performance issues**:
   - Prefetching `items__material` is good, but nested relations need monitoring for overhead.
