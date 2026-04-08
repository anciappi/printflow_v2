#!/bin/bash

# --- CONFIGURACIÓN ---
DB_NAME="printflow_db"
DB_USER="printflow_user"

echo "🛑  INICIANDO RESETEO TOTAL DE LA APP (MULTI-TENANT)..."

# 1. Borrar archivos de migración
echo "🧹  Limpiando archivos de migraciones anteriores..."
find . -path "*/migrations/*.py" -not -name "__init__.py" -not -path "*/venv/*" -delete
find . -path "*/migrations/*.pyc" -not -path "*/venv/*" -delete

# 2. Eliminar y Recrear la Base de Datos
echo "🔥  Reiniciando Base de Datos PostgreSQL..."
sudo -u postgres psql -c "
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '$DB_NAME'
  AND pid <> pg_backend_pid();" > /dev/null 2>&1

sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"

# 3. Reconstruir migraciones
echo "🏗️   Creando nuevas migraciones..."
python manage.py makemigrations

# 4. Aplicar migraciones al schema public (SHARED_APPS)
echo "🚀  Aplicando migraciones shared (schema public)..."
python manage.py migrate_schemas --shared

# 4b. Aplicar RLS policies
echo "🔒  Aplicando Row Level Security (RLS)..."
sudo -u postgres psql -d printflow_db -f scripts/rls_setup.sql
echo "✅  RLS aplicado."

# 5. Crear tenant público (obligatorio para django-tenants)
echo "🏢  Creando tenant público (PrintFlow)..."
python manage.py shell -c "
from tenants.models import PrintShop, Domain
t = PrintShop(schema_name='public', name='PrintFlow', plan='enterprise')
t.save()
Domain.objects.create(domain='localhost', tenant=t, is_primary=True)
print('✅ Tenant público creado.')
"

# 6. Crear superusuario global (tenant=None = acceso a todo)
echo "👑  Creando Superusuario global..."
python manage.py shell -c "
from users.models import User
User.objects.create_superuser(
    username='anciappi',
    email='anciappi@printflow.com',
    password='anc31763534...',
    tenant=None,
    is_staff=True,
)
print('✅ Superusuario global creado (tenant=None).')
"

# 7. Crear tenant Grupo Velton con sus branches
echo "🏭  Creando tenant Grupo Velton..."
python manage.py shell -c "
from tenants.models import PrintShop, Domain, Branch
velton = PrintShop(schema_name='velton', name='Grupo Velton', plan='pro')
velton.save()
Domain.objects.create(domain='velton.localhost', tenant=velton, is_primary=True)
Branch.objects.create(tenant=velton, name='Velton')
Branch.objects.create(tenant=velton, name='Magtik')
print('✅ Tenant Grupo Velton creado.')
"

# 8. Crear usuario operativo para Velton
echo "👤  Creando usuario operativo en Grupo Velton..."
python manage.py shell -c "
from django.db import connection
from users.models import User
from tenants.models import PrintShop

velton = PrintShop.objects.get(schema_name='velton')

# Set RLS context before creating user
with connection.cursor() as cursor:
    cursor.execute(\"SELECT set_config('app.current_tenant_id', %s, false)\", [str(velton.id)])

User.objects.create_user(
    username='velton_admin',
    email='admin@velton.com',
    password='velton1234',
    role='ADMIN',
    tenant=velton,
)
print('✅ Usuario velton_admin creado para Grupo Velton.')
"


# 7. Crear tenant Salleo SRL con sus branches
echo "🏭  Creando tenant Salleo..."
python manage.py shell -c "
from tenants.models import PrintShop, Domain, Branch
velton = PrintShop(schema_name='salleo', name='Salleo SRL', plan='pro')
velton.save()
Domain.objects.create(domain='salleo.localhost', tenant=velton, is_primary=True)
print('✅ Tenant Salleo SRL creado.')
"

# 8. Crear usuario operativo para Salleo
echo "👤  Creando usuario operativo en Salleo..."
python manage.py shell -c "
from django.db import connection
from users.models import User
from tenants.models import PrintShop

salleo = PrintShop.objects.get(schema_name='salleo')

# Set RLS context before creating user
with connection.cursor() as cursor:
    cursor.execute(\"SELECT set_config('app.current_tenant_id', %s, false)\", [str(salleo.id)])

User.objects.create_user(
    username='salleo_admin',
    email='admin@salleo.com',
    password='salleo1234',
    role='ADMIN',
    tenant=salleo,
)
print('✅ Usuario salleo_admin creado para Salleo SRL.')
"



echo ""
echo "✅  ¡LISTO! Sistema reseteado y configurado para desarrollo."
echo ""
echo "   Accesos disponibles:"
echo "   → Admin público:  http://localhost:8001/admin/"
echo "   → Grupo Velton:   http://velton.localhost:8001/"
echo "   → Salleo SRL:   http://salleo.localhost:8001/"
echo ""
echo "   Recordá agregar a /etc/hosts:"
echo "   127.0.0.1  velton.localhost"
echo "   127.0.0.1  salleo.localhost"