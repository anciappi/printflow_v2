import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

try:
    from django_tenants.utils import get_tenant_model
    Tenant = get_tenant_model()
    tenants = Tenant.objects.exclude(schema_name='public')
    schemas = [t.schema_name for t in tenants]
except ImportError:
    schemas = [None] # Not using django-tenants

from products.models import Color

def seed():
    colors = ['Cyan', 'Magenta', 'Amarillo', 'Negro']
    for color in colors:
        Color.objects.get_or_create(name=color, defaults={'is_standard': True})
    print("Seeded CMYK in current context.")

if schemas == [None]:
    seed()
else:
    from django.db import connection
    for schema in schemas:
        connection.set_schema(schema)
        print(f"Seeding schema: {schema}")
        seed()
    connection.set_schema_to_public()
