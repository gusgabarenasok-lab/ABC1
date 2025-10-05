#!/usr/bin/env bash
# Script de build para Render

set -o errexit  # Exit on error

echo "[BUILD] Instalando dependencias..."
pip install -r requirements.txt

echo "[BUILD] Recolectando archivos estaticos..."
python manage.py collectstatic --noinput

echo "[BUILD] Sincronizando base de datos (creando todas las tablas)..."
python manage.py migrate --run-syncdb --noinput

echo "[BUILD] Aplicando migraciones forzadamente..."
python manage.py migrate --fake-initial --noinput

echo "[BUILD] Creando superusuario si no existe..."
python manage.py create_superuser_if_none

echo "[BUILD] Build completado exitosamente!"
