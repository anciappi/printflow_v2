#!/bin/bash

echo "🚀 Iniciando limpieza total SEGURA de PrintFlow v2..."

# 1. Eliminar la base de datos
if [ -f db.sqlite3 ]; then
    rm db.sqlite3
    echo "✅ Base de datos eliminada."
fi

# 2. Eliminar migraciones EXCLUYENDO el venv
echo "📂 Limpiando migraciones del proyecto..."
find . -not -path "./venv/*" -path "*/migrations/*.py" -not -name "__init__.py" -delete

# 3. Eliminar caché EXCLUYENDO el venv
echo "🐍 Eliminando __pycache__ del proyecto..."
find . -not -path "./venv/*" -name "__pycache__" -type d -exec rm -rf {} +

# 4. Re-generar todo
echo "🛠️  Generando nuevas migraciones..."
python3 manage.py makemigrations

echo "⚙️  Aplicando migraciones..."
python3 manage.py migrate

# 5. Superusuario
export DJANGO_SUPERUSER_PASSWORD=anc31763534
export DJANGO_SUPERUSER_USERNAME=anciappi
export DJANGO_SUPERUSER_EMAIL=anciappi@printflow.com
python3 manage.py createsuperuser --no-input

echo "✨ Entorno restaurado correctamente."