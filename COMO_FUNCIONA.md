# 📖 Cómo funciona el proyecto — BarberShop Reservas

---

##  Estructura general

Este es un proyecto web hecho con **Django** (Python). Django sigue el patrón **MTV**:

```
Model  →  los datos (base de datos)
Template → lo que ve el usuario (HTML)
View   →  la lógica que conecta ambos
```

Cuando el usuario entra a una URL, Django busca en `urls.py` qué vista ejecutar,
la vista consulta los modelos, y devuelve un template con los datos.

```
Usuario escribe URL
      ↓
urls.py  →  encuentra la vista correcta
      ↓
views.py / dashboard_views.py  →  lógica + consulta a la BD
      ↓
Template HTML  →  se muestra en el navegador
```

---

## 🗄️ 1. Los Modelos (models.py) — La base de datos

Son las 4 tablas que usa el proyecto:

### Usuario
Extiende el usuario de Django agregando:
- `telefono` — teléfono del usuario
- `direccion` — dirección
- `rol` — puede ser **CLIENTE**, **BARBERO** o **ADMIN**

Cada persona que se registra es un Usuario. El rol define qué puede hacer.

### Barbero
Un barbero ES un Usuario (relación OneToOne), más:
- `especialidad` — en qué es bueno (cortes, barbas, etc.)
- `disponible` — si aparece o no para reservas

### Servicio
Lo que ofrece la barbería:
- `nombre` — ej: "Corte clásico"
- `precio` — cuánto cuesta
- `duracion_minutos` — cuánto tarda
- `activo` — si está visible para los clientes

### Reserva
El corazón del sistema. Une todo:
- `cliente` → quién reservó (Usuario)
- `barbero` → con quién (Barbero)
- `servicio` → qué servicio (Servicio)
- `fecha` y `hora` → cuándo
- `estado` → PENDIENTE / CONFIRMADA / RECHAZADA / CANCELADA

> ⚠️ No se puede hacer doble reserva: un barbero no puede tener
> dos reservas el mismo día a la misma hora.

---

## 🔗 2. Las URLs (urls.py) — El mapa del sitio

Define qué URL lleva a qué vista. Hay dos grupos:

### Sitio público (cualquier persona)
| URL | Qué hace |
|-----|----------|
| `/` | Página de inicio |
| `/login/` | Iniciar sesión |
| `/register/` | Crear cuenta |
| `/logout/` | Cerrar sesión |
| `/servicios/` | Ver servicios |
| `/barberos/` | Ver barberos |
| `/reservas/` | Hacer una reserva |
| `/confirmacion/<id>/` | Ver confirmación de reserva |
| `/mis-reservas/` | Ver mis reservas (requiere login) |
| `/cancelar/<id>/` | Cancelar una reserva |
| `/agenda/` | Agenda del barbero (solo barberos) |

### Dashboard admin (solo ADMIN o superusuario)
| URL | Qué hace |
|-----|----------|
| `/dashboard/` | Resumen general con estadísticas |
| `/dashboard/reservas/` | Ver y filtrar todas las reservas |
| `/dashboard/barberos/` | Gestionar barberos |
| `/dashboard/servicios/` | Gestionar servicios |
| `/dashboard/usuarios/` | Gestionar usuarios |

Cada sección tiene también URLs para crear, editar y eliminar.

---

## ⚙️ 3. Las Vistas — La lógica

### views.py — Sitio público

**`home`**
Carga servicios activos y barberos disponibles y los muestra en la página de inicio.

**`register_view`**
- Si es GET: muestra el formulario de registro
- Si es POST: valida que las contraseñas coincidan, que el usuario no exista,
  crea el usuario con rol CLIENTE y lo loguea automáticamente

**`login_view`**
- Si es GET: muestra el formulario
- Si es POST: usa `authenticate()` de Django para verificar usuario/contraseña,
  si es correcto llama `login()` y redirige al inicio

**`logout_view`**
Llama `logout()` y redirige al login.

**`reservar_view`** (requiere login)
- GET: muestra el formulario con barberos y servicios disponibles
- POST: verifica que no haya doble reserva, crea la reserva con estado PENDIENTE
  y redirige a la confirmación

**`mis_reservas_view`** (requiere login)
Muestra todas las reservas del usuario logueado, ordenadas por más reciente.

**`cancelar_reserva_view`** (requiere login)
Solo permite cancelar si el estado es PENDIENTE. Cambia el estado a CANCELADA.

**`agenda_view`** (solo BARBERO)
Muestra todas las reservas asignadas al barbero logueado.

**`cambiar_estado_reserva`** (solo BARBERO)
Permite al barbero confirmar o rechazar una reserva PENDIENTE.

---

### dashboard_views.py — Panel de administración

Todas las vistas verifican primero si el usuario es ADMIN con `es_admin()`.
Si no lo es, redirige al inicio.

**`dashboard_home`**
Cuenta totales de reservas, barberos, clientes y servicios.
Muestra las últimas 10 reservas en una tabla.

**`dashboard_reservas`**
Lista todas las reservas con filtros por estado, barbero y fecha.
Los filtros llegan por GET (`?estado=PENDIENTE&barbero=2`).

**`dashboard_reserva_editar`**
- GET: muestra el formulario con los datos actuales de la reserva
- POST: actualiza todos los campos y guarda

**`dashboard_reserva_eliminar`**
- GET: muestra pantalla de confirmación
- POST: elimina la reserva

El mismo patrón GET/POST se repite para barberos, servicios y usuarios.

**`dashboard_servicio_toggle`**
Activa o desactiva un servicio con un solo clic (invierte el valor de `activo`).

**`dashboard_barbero_crear`**
Crea primero el Usuario con rol BARBERO y luego crea el Barbero vinculado.
Esto es necesario porque Barbero depende de Usuario.

**`dashboard_usuario_eliminar`**
Tiene una protección extra: no puedes eliminar tu propia cuenta.

---

## 🎨 4. Los Templates — Lo que ve el usuario

### Layouts (plantillas base)
- `layouts/base.html` — base del sitio público (navbar, footer)
- `layouts/dashboard_base.html` — base del dashboard (sidebar, navbar admin)

Todos los demás templates extienden uno de estos dos con `{% extends %}`.

### Sitio público
```
home.html          → página de inicio
login.html         → formulario de login
register.html      → formulario de registro
servicios.html     → lista de servicios
barberos.html      → lista de barberos
reservas.html      → formulario de reserva
confirmacion.html  → confirmación de reserva
Mis_Reservas.html  → mis reservas
agenda.html        → agenda del barbero
clientes.html      → lista de clientes (solo admin)
```

### Dashboard
```
dashboard/home.html              → resumen con tarjetas y tabla
dashboard/reservas_list.html     → tabla de reservas con filtros
dashboard/reserva_form.html      → formulario crear/editar reserva
dashboard/barberos_list.html     → tabla de barberos
dashboard/barbero_form.html      → formulario crear/editar barbero
dashboard/servicios_list.html    → tabla de servicios
dashboard/servicio_form.html     → formulario crear/editar servicio
dashboard/usuarios_list.html     → tabla de usuarios
dashboard/usuario_form.html      → formulario crear/editar usuario
dashboard/confirmar_eliminar.html → pantalla de confirmación al eliminar
```

---

## 🎨 5. Los CSS — El diseño

```
static/css/
├── base.css           → estilos globales (navbar, footer, botones, cards)
├── home.css           → estilos de la página de inicio
├── login_register.css → estilos del login y registro
├── servicios.css      → estilos de la página de servicios
├── barberos.css       → estilos de la página de barberos
├── reservas.css       → estilos del formulario de reserva
├── confirmacion.css   → estilos de la confirmación
├── mis_reservas.css   → estilos de mis reservas
├── agenda.css         → estilos de la agenda del barbero
├── clientes.css       → estilos de la lista de clientes
└── dashboard/
    ├── dashboard.css          → estilos compartidos del dashboard
    │                            (layout, sidebar, tablas, badges, botones, forms)
    ├── home.css               → estilos extra para el resumen
    ├── reservas_list.css      → estilos extra para lista de reservas
    ├── reserva_form.css       → estilos extra para formulario de reserva
    ├── barberos_list.css      → estilos extra para lista de barberos
    ├── barbero_form.css       → estilos extra para formulario de barbero
    ├── servicios_list.css     → estilos extra para lista de servicios
    ├── servicio_form.css      → estilos extra para formulario de servicio
    ├── usuarios_list.css      → estilos extra para lista de usuarios
    ├── usuario_form.css       → estilos extra para formulario de usuario
    └── confirmar_eliminar.css → estilos extra para confirmación de eliminar
```

Cada template del dashboard carga `dashboard.css` (desde el base) más
su propio CSS específico via `{% block extra_css %}`.

---

## 🔐 6. Los roles y permisos

| Rol | Puede hacer |
|-----|-------------|
| **CLIENTE** | Registrarse, hacer reservas, ver sus reservas, cancelar reservas pendientes |
| **BARBERO** | Todo lo del cliente + ver su agenda + confirmar/rechazar reservas |
| **ADMIN** | Todo + acceso al dashboard completo (gestionar todo) |
| **Superusuario** | Igual que ADMIN + acceso al admin de Django (`/admin/`) |

---

## 🔄 7. Flujo completo de una reserva

```
1. Cliente entra a /reservas/
2. Elige barbero, servicio, fecha y hora
3. Envía el formulario (POST)
4. Django verifica que no haya doble reserva
5. Crea la Reserva con estado = PENDIENTE
6. Redirige a /confirmacion/<id>/
7. El barbero entra a /agenda/ y ve la reserva pendiente
8. El barbero hace clic en "Confirmar" o "Rechazar"
9. Django cambia el estado a CONFIRMADA o RECHAZADA
10. El cliente puede ver el estado actualizado en /mis-reservas/
11. Si quiere, puede cancelar si sigue PENDIENTE
```

---

## ⚙️ 8. Configuración (settings.py)

Los puntos más importantes:

- `AUTH_USER_MODEL` — le dice a Django que use tu modelo `Usuario` en vez del de Django
- `INSTALLED_APPS` — registra tu app `reservaciones_barberia`
- `TEMPLATES / APP_DIRS: True` — Django busca templates dentro de cada app automáticamente
- `STATICFILES_DIRS` — le dice a Django dónde están los archivos CSS/imágenes
- `LOGIN_URL` — si alguien intenta entrar a una página que requiere login, lo manda aquí
- `DATABASES` — usa SQLite (un archivo `db.sqlite3`) como base de datos

---

## 🚀 9. Cómo correr el proyecto

```bash
# 1. Activar el entorno virtual
.venv\Scripts\activate

# 2. Aplicar migraciones (primera vez o cuando cambias models.py)
python manage.py migrate

# 3. Crear superusuario (primera vez)
python manage.py createsuperuser

# 4. Correr el servidor
python manage.py runserver
```

Luego abre `http://127.0.0.1:8000/` en el navegador.

El dashboard está en `http://127.0.0.1:8000/dashboard/`
(necesitas estar logueado como ADMIN o superusuario).
