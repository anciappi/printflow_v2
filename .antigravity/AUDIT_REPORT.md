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
