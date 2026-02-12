#!/bin/bash

# --- CONFIGURACIÓN ---
DB_NAME="printflow_db"
DB_USER="printflow_user"

echo "🛑  INICIANDO RESETEO TOTAL DE LA APP (POSTGRESQL)..."

# 1. Borrar archivos de migración (VERSIÓN SEGURA)
# Agregamos: -not -path "*/venv/*" para que NO entre en el entorno virtual
echo "🧹  Limpiando archivos de migraciones anteriores..."
find . -path "*/migrations/*.py" -not -name "__init__.py" -not -path "*/venv/*" -delete
find . -path "*/migrations/*.pyc" -not -path "*/venv/*" -delete

# ... (El resto del script sigue igual) ...
# 2. Eliminar y Recrear la Base de Datos...
echo "🔥  Reiniciando Base de Datos PostgreSQL..."

sudo -u postgres psql -c "
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '$DB_NAME'
  AND pid <> pg_backend_pid();" > /dev/null 2>&1

sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"

# 3. Reconstruir Django
echo "🏗️   Creando nuevas migraciones..."
python manage.py makemigrations

echo "🚀  Aplicando migraciones a la nueva DB..."
python manage.py migrate

# 4. Crear Superusuario Automático
echo "👑  Creando Superusuario (admin / admin)..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('anciappi', 'anciappi@printflow.com', 'anc31763534...')"

echo "✅  ¡LISTO! Sistema reseteado correctamente."