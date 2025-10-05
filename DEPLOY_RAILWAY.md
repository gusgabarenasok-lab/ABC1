# 🚂 Guía de Deploy en Railway - SIPROSA MES

## 📋 Checklist Pre-Deploy

Antes de hacer push a GitHub, verifica:

- [x] `settings.py` limpio y consolidado
- [x] `.gitignore` actualizado
- [x] `requirements.txt` con todas las dependencias
- [x] `runtime.txt` con versión de Python
- [ ] Variables de entorno configuradas en Railway
- [ ] PostgreSQL conectado en Railway
- [ ] Build commands correctos en Railway

---

## 🔧 PASO 1: Configurar el Proyecto en Railway

### 1.1. Crear Nuevo Proyecto
1. Ve a [Railway.app](https://railway.app/)
2. Click en "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Conecta tu repositorio `ABC1`

### 1.2. Agregar PostgreSQL
1. Dentro del proyecto, click en "+ New"
2. Selecciona "Database" → "PostgreSQL"
3. Railway automáticamente creará las variables de conexión

---

## 🔐 PASO 2: Configurar Variables de Entorno

Ve a tu servicio Django en Railway → **Variables** y agrega:

```bash
# Generar con: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY=tu-secret-key-generada-aqui

ENVIRONMENT=production
DEBUG=False

# Railway detecta automáticamente el dominio
ALLOWED_HOSTS=.railway.app

# Si tienes un frontend, agrega su URL
CORS_ALLOWED_ORIGINS=https://tu-frontend.railway.app
CSRF_TRUSTED_ORIGINS=https://tu-frontend.railway.app
```

### Variables de Base de Datos

Railway provee automáticamente estas variables cuando conectas PostgreSQL:
- `DATABASE_URL`
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`

**Si Railway no las detecta automáticamente**, agrégalas manualmente:

```bash
DB_NAME=${{Postgres.PGDATABASE}}
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
```

---

## ⚙️ PASO 3: Configurar Build Settings

Railway debería detectar automáticamente tu proyecto Django usando `nixpacks.toml`, pero verifica:

### 3.1. Build Command
```bash
python manage.py collectstatic --noinput && python manage.py migrate --noinput
```

### 3.2. Start Command
```bash
gunicorn backend.wsgi --bind 0.0.0.0:$PORT
```

### 3.3. Root Directory
```
/
```

---

## 📦 PASO 4: Archivos Necesarios (Ya los tienes)

### ✅ `requirements.txt`
```txt
Django==5.2.7
djangorestframework==3.16.1
djangorestframework-simplejwt==5.5.1
psycopg2-binary==2.9.10
django-cors-headers==4.9.0
python-dotenv==1.1.1
gunicorn==23.0.0
PyJWT==2.10.1
```

### ✅ `runtime.txt`
```txt
python-3.10.12
```

### ✅ `Procfile`
```
web: gunicorn backend.wsgi --log-file -
```

### ✅ `nixpacks.toml`
```toml
[phases.setup]
nixPkgs = ["python310", "postgresql"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = [
    "python manage.py collectstatic --noinput",
    "python manage.py migrate --noinput"
]

[start]
cmd = "gunicorn backend.wsgi --bind 0.0.0.0:$PORT"
```

---

## 🚀 PASO 5: Hacer Deploy

### 5.1. Commit y Push
```bash
git add .
git commit -m "refactor: limpiar settings y mejorar serializers"
git push origin main
```

### 5.2. Railway Detectará Automáticamente
Railway iniciará el build automáticamente al detectar el push.

### 5.3. Ver Logs
En Railway, ve a tu servicio → **Deployments** → Click en el último deploy → **View Logs**

---

## 🧪 PASO 6: Verificar el Deploy

### 6.1. Obtener la URL
En Railway, ve a **Settings** → **Domains** → Copia tu URL (ej: `https://abc1-production.up.railway.app`)

### 6.2. Probar Health Check
```bash
curl https://tu-app.railway.app/api/health/
```

Deberías recibir:
```json
{
  "status": "ok",
  "database": true,
  "debug": false,
  "django_version": "5.2.7",
  "server_time": "2025-10-05T...",
  "environment": "production"
}
```

### 6.3. Crear Superusuario
En Railway, ve a tu servicio → **Run Command**:
```bash
python manage.py createsuperuser
```

O conecta por SSH:
```bash
railway run python manage.py createsuperuser
```

---

## 🔍 PASO 7: Probar la API

### Obtener Token
```bash
curl -X POST https://tu-app.railway.app/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "tu-password"
  }'
```

### Listar Máquinas
```bash
curl https://tu-app.railway.app/api/maquinas/ \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

---

## 🐛 Troubleshooting

### Error: "Application failed to respond"
- Verifica que `ALLOWED_HOSTS` incluya `.railway.app`
- Revisa logs en Railway

### Error: "Database connection refused"
- Verifica que PostgreSQL esté conectado
- Verifica las variables `DB_*` en Variables

### Error 500 en producción
- Verifica los logs: Railway → View Logs
- Asegúrate de que `DEBUG=False`
- Revisa que `SECRET_KEY` esté configurada

### Las migraciones no se aplican
- Ejecuta manualmente:
```bash
railway run python manage.py migrate
```

---

## 📝 Comandos Útiles de Railway CLI

### Instalar Railway CLI (opcional)
```bash
npm i -g @railway/cli
railway login
```

### Ver Logs en Tiempo Real
```bash
railway logs
```

### Ejecutar Comandos Django
```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python manage.py shell
```

---

## ✅ Checklist Post-Deploy

Una vez deployado exitosamente:

- [ ] Health check responde correctamente
- [ ] PostgreSQL conectado (verifica en `/api/health/`)
- [ ] Puedes obtener JWT token
- [ ] Admin panel accesible en `/admin/`
- [ ] Endpoints de API funcionan con autenticación
- [ ] Variables de entorno correctas (DEBUG=False en producción)
- [ ] CORS configurado si tienes frontend

---

## 🎯 Próximos Pasos

1. **Crear usuarios y grupos** en el Django Admin
2. **Cargar datos iniciales** de máquinas
3. **Conectar frontend** (Next.js)
4. **Expandir funcionalidad** según el roadmap del MES

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs en Railway
2. Verifica las variables de entorno
3. Comparte el error exacto para debugging

