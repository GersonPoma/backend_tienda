# 🏪 Backend Tienda - Sistema Multi-Tenant

Sistema de tienda online multi-tenant con Django, PostgreSQL y JWT. Cada empresa tiene su propio esquema de base de datos completamente aislado.

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación](#instalación)
3. [Configuración Inicial](#configuración-inicial)
4. [Migraciones de Base de Datos](#migraciones-de-base-de-datos)
5. [Setup del Sistema](#setup-del-sistema)
6. [Iniciar el Servidor](#iniciar-el-servidor)
7. [Endpoints Disponibles](#endpoints-disponibles)
8. [Ejemplos de Uso](#ejemplos-de-uso)

---

## 📦 Requisitos Previos

Asegúrate de tener instalado:

- **Python 3.10+** - [Descargar](https://www.python.org/downloads/)
- **PostgreSQL 12+** - [Descargar](https://www.postgresql.org/download/)
- **Git** - [Descargar](https://git-scm.com/download)
- **Postman** (Opcional, para probar la API)

### Verificar instalación:

```bash
python --version
psql --version
git --version
```

---

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd backend_tienda
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

Si `requirements.txt` no existe, instala manualmente:

```bash
pip install django==5.2.12
pip install django-tenants==3.10.1
pip install psycopg2-binary==2.9.9
pip install djangorestframework==3.17.1
pip install djangorestframework-simplejwt==5.5.1
pip install django-cors-headers==4.9.0
pip install django-environ==0.11.2
```

---

## 🔧 Configuración Inicial

### 1. Crear Archivo .env

Crea un archivo `.env` en la raíz del proyecto:

```bash
# En Windows
copy .env.example .env

# En Linux/Mac
cp .env.example .env
```

O crea manualmente con este contenido:

```env
# Seguridad
DEBUG=True
SECRET_KEY='django-insecure-8b2*2_g#7e%o7^2f5q2m-+53n)x4$73m&3u6ve5uf3k_$+9ux!'

# Base de Datos
DB_NAME=tienda_online
DB_USER=postgres
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5432

# Dominios CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:4200,http://localhost:8080

# Email (opcional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 2. Crear Base de Datos PostgreSQL

```bash
# Conectar a PostgreSQL
psql -U postgres

# Dentro de psql, ejecutar:
CREATE DATABASE tienda_online;
\q
```

O desde terminal (Windows):

```bash
psql -U postgres -c "CREATE DATABASE tienda_online;"
```

### 3. Configurar Archivo HOSTS

Para que los subdominios locales funcionen, agrega entradas al archivo HOSTS.

**Windows:**
```
Archivo: C:\Windows\System32\drivers\etc\hosts
Agrega:
127.0.0.1 localhost
127.0.0.1 tienda-amiga.localhost
127.0.0.1 tienda-sol.localhost
```

**Linux/Mac:**
```bash
sudo nano /etc/hosts

Agrega:
127.0.0.1 localhost
127.0.0.1 tienda-amiga.localhost
127.0.0.1 tienda-sol.localhost

Guarda: Ctrl+O, Enter, Ctrl+X
```

**Verificar:**
```bash
ping tienda-amiga.localhost
```

---

## 🗄️ Migraciones de Base de Datos

### 1. Crear Migraciones

```bash
python manage.py makemigrations
```

### 2. Migrar Esquema Público

```bash
python manage.py migrate_schemas --shared
```

---

## ⚙️ Setup del Sistema

### 1. Crear Tenant Admin (Esquema Público)

```bash
python setup_admin_tenant.py
```

Este script:
- ✓ Crea empresa "Admin" con schema_name='public'
- ✓ Registra dominio 127.0.0.1
- ✓ Registra dominio localhost

### 2. Crear Super Usuario del Admin Público

```bash
python manage.py createsuperuser
```

Ejemplo de credenciales:
```
Username: admin_public
Email: admin@backend-tienda.com
Password: admin123456
```

### 3. Crear Tenant de Prueba (Tienda Amiga)

```bash
python create_tenant.py
```

Este script:
- ✓ Crea empresa "Tienda Amiga" con schema_name='tienda_amiga'
- ✓ Registra dominio tienda-amiga.localhost
- ✓ Crea el schema automáticamente en PostgreSQL

### 4. Crear Super Usuario del Tenant Tienda Amiga

**Opción A: Script automático (RECOMENDADO)**

```bash
python create_tenant_superuser.py
```

Te pedirá interactivamente:
```
Username: admin
Email: admin@tienda-amiga.com
Password (mín 8 caracteres): ••••••••
Confirmar password: ••••••••
```

**Opción B: Con parámetros directos**

```bash
python create_tenant_superuser.py admin admin@tienda-amiga.com tienda2024
```

**Nota:** Para crear super usuarios en otros tenants, usa la API `/api/empresas/register/`

Ejemplo de credenciales:
```
Username: admin
Email: admin@tienda-amiga.com
Password: tienda2024
```

### 5. Crear Grupos de Usuarios (Opcional)

```bash
python manage.py shell --tenant tienda_amiga
```

Dentro de la consola:

```python
from django.contrib.auth.models import Group

# Crear grupos
Group.objects.create(name='Cliente')
Group.objects.create(name='Vendedor')
Group.objects.create(name='Gerente')

print("✓ Grupos creados exitosamente")
exit()
```

---

## 🎯 Iniciar el Servidor

```bash
python manage.py runserver
```

El servidor se iniciará en `http://localhost:8000`

---

## 🌐 Endpoints Disponibles

### Admin Django

```
http://localhost:8000/admin/                      (Admin Público)
http://tienda-amiga.localhost:8000/admin/         (Admin Tienda Amiga)
http://tienda-sol.localhost:8000/admin/           (Admin Tienda Sol - si existe)
```

### API - Autenticación

```
POST /api/login/                    - Iniciar sesión (sin autenticación)
```

### API - Usuarios (requiere JWT)

```
GET    /api/usuarios/               - Listar usuarios
GET    /api/usuarios/{id}/          - Obtener usuario
POST   /api/usuarios/               - Crear usuario
PUT    /api/usuarios/{id}/          - Actualizar usuario
DELETE /api/usuarios/{id}/          - Eliminar usuario
```

### API - Clientes (sin autenticación)

```
POST /api/usuarios/registrar_cliente/  - Registrar cliente
```

### API - Empresas (sin autenticación)

```
POST /api/empresas/register/          - Registrar empresa
GET  /api/empresas/listar_todas/      - Listar empresas
GET  /api/empresas/{id}/              - Obtener empresa
```

---

## 💡 Ejemplos de Uso

### 1. Login (Obtener Token JWT)

**Request:**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "tienda2024"
  }'
```

**Response:**
```json
{
    "success": true,
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "usuario_id": 1,
    "username": "admin",
    "nombre_completo": "Admin Admin"
}
```

### 2. Listar Usuarios (con Token)

```bash
curl -X GET http://localhost:8000/api/usuarios/ \
  -H "Authorization: Bearer <access_token>"
```

### 3. Registrar Cliente

```bash
curl -X POST http://localhost:8000/api/usuarios/registrar_cliente/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "cliente123",
    "password": "MiPassword123!",
    "nombre": "Juan",
    "apellido": "Pérez",
    "fecha_nacimiento": "1990-01-15"
  }'
```

### 4. Registrar Empresa

```bash
curl -X POST http://localhost:8000/api/empresas/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Mi Tienda",
    "correo": "info@mitienda.com",
    "super_admin": {
      "username": "admin",
      "email": "admin@mitienda.com",
      "password": "Password123!",
      "password_confirm": "Password123!"
    }
  }'
```

---

## 📝 Estructura del Proyecto

```
backend_tienda/
├── apps_publicas/
│   └── empresas/              (Registro de empresas)
│       ├── models.py          (Empresa, Dominio)
│       ├── views.py           (API REST)
│       ├── serializers.py     (Validación)
│       ├── services.py        (Lógica de negocio)
│       └── urls.py
│
├── apps_privadas/
│   └── seguridad/             (Usuarios y autenticación)
│       ├── models.py          (Usuario - heredado de AbstractUser)
│       ├── views.py           (ViewSet de usuarios + login)
│       ├── serializers.py     (Serializers de usuarios)
│       ├── login_serializers.py (JWT personalizado)
│       ├── services.py        (CRUD y registro de clientes)
│       └── urls.py
│
├── backend_tienda/
│   ├── settings.py            (Configuración Django)
│   ├── urls.py                (Rutas principales)
│   └── wsgi.py
│
├── .env                        (Variables de entorno)
├── manage.py                   (CLI de Django)
└── requirements.txt            (Dependencias)
```

---

## 🐛 Troubleshooting

### Error: "No tenant found for hostname"

**Solución:** Ejecuta `python setup_admin_tenant.py`

### Error: "psycopg2 error"

**Solución:** Verifica que PostgreSQL esté corriendo y las credenciales en .env sean correctas

### Error: "Module not found"

**Solución:** Activa el entorno virtual y ejecuta `pip install -r requirements.txt`

### Puerto 8000 ocupado

**Solución:** Usa otro puerto
```bash
python manage.py runserver 8001
```

### El subdominio no funciona

**Solución:** Verifica que:
1. El archivo HOSTS esté actualizado
2. Limpia el cache del navegador
3. Reinicia el navegador

---

## 📚 Documentación Adicional

- **API_REGISTRO_EMPRESAS.md** - Guía completa de la API
- **CREAR_SUPER_USUARIOS.md** - Crear usuarios por tenant
- **SETUP_MULTITENANT.md** - Documentación técnica multi-tenant
- **RESUMEN_CONFIGURACION.md** - Configuración detallada
- **CORS_POSTMAN_ANGULAR.md** - Integración con Postman y Angular

---

## 🎯 Checklist Rápido

- [ ] Python 3.10+ instalado
- [ ] PostgreSQL instalado y corriendo
- [ ] Base de datos `tienda_online` creada
- [ ] .env configurado
- [ ] HOSTS actualizado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Migraciones ejecutadas (`python manage.py migrate_schemas --shared`)
- [ ] Tenant Admin creado (`python setup_admin_tenant.py`)
- [ ] Super usuario creado
- [ ] Servidor iniciado (`python manage.py runserver`)

---

## 🚀 ¡Listo para Desarrollar!

El sistema está completamente configurado y listo para:
- Registrar nuevas empresas
- Crear y gestionar usuarios
- Autenticarse con JWT
- Desarrollar features específicas por tenant

Accede a http://localhost:8000/admin/ para comenzar.

---

**Última actualización:** Abril 2026  
**Versión:** 1.0.0  
**Status:** ✅ Producción Lista


