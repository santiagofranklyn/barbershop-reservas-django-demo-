# 🛠️ Guía: Cómo construir el Dashboard Admin desde cero

> Esta guía asume que ya tienes el proyecto Django funcionando con el
> admin de Django (`/admin/`) y quieres reemplazarlo por tu propio
> dashboard personalizado.

---

## 🧠 ¿Por qué hacer un dashboard propio en vez de usar el de Django?

El admin de Django (`/admin/`) es genérico y técnico. Está pensado para
desarrolladores, no para el dueño de una barbería. Tu dashboard propio:

- Tiene el diseño de tu proyecto (colores, fuentes, estilo)
- Muestra solo lo que necesita el negocio
- Tiene estadísticas visuales (tarjetas con conteos)
- Es más fácil de usar para alguien sin conocimientos técnicos

---

## 📋 Orden de los pasos

```
1. Planificar qué va a tener el dashboard
2. Crear el archivo dashboard_views.py
3. Crear la función de seguridad es_admin()
4. Crear las vistas una por una
5. Registrar las URLs en urls.py
6. Crear el layout base del dashboard
7. Crear los templates HTML
8. Crear los archivos CSS
9. Conectar el link en el navbar del sitio
10. Probar todo
```

---

## 📝 Paso 1 — Planificar qué va a tener el dashboard

Antes de escribir una sola línea de código, decide qué secciones necesitas.
En este proyecto el dashboard tiene:

- **Resumen** — estadísticas generales del negocio
- **Reservas** — ver, editar y eliminar todas las reservas
- **Barberos** — crear, editar y eliminar barberos
- **Servicios** — crear, editar, activar/desactivar y eliminar servicios
- **Usuarios** — crear, editar y eliminar usuarios

Por cada sección necesitarás:
- Una vista para listar
- Una vista para crear
- Una vista para editar
- Una vista para eliminar

---

## 📄 Paso 2 — Crear dashboard_views.py

**¿Por qué un archivo separado y no en views.py?**

`views.py` ya tiene las vistas del sitio público. Si metes todo ahí
el archivo se vuelve enorme y difícil de leer. Separarlo en
`dashboard_views.py` mantiene el código organizado.

Crea el archivo en la misma carpeta que `views.py`:

```
reservaciones_barberia/
├── views.py            ← vistas del sitio público (ya existe)
└── dashboard_views.py  ← vistas del dashboard (nuevo)
```

Empieza el archivo con los imports necesarios:

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Barbero, Servicio, Reserva, Usuario
```

**¿Qué importa cada línea?**
- `render` — convierte un template HTML en una respuesta para el navegador
- `redirect` — manda al usuario a otra URL
- `get_object_or_404` — busca un objeto en la BD, si no existe devuelve error 404
- `login_required` — decorador que bloquea la vista si no estás logueado
- `messages` — para mostrar mensajes de éxito o error al usuario
- Los modelos — para poder consultar la base de datos

---

## 🔐 Paso 3 — Crear la función de seguridad

Esta es la función más importante. Va al inicio de `dashboard_views.py`:

```python
def es_admin(user):
    return user.is_authenticated and (user.is_superuser or user.rol == "ADMIN")
```

**¿Por qué hacerla función y no repetir el código?**

Porque la vas a usar en CADA vista del dashboard. Si la escribes como
función, solo la defines una vez y la llamas en todas partes.
Si mañana cambias la lógica de permisos, solo cambias un lugar.

**¿Cómo se usa en cada vista?**

```python
@login_required
def dashboard_home(request):
    if not es_admin(request.user):          # ← verificación de seguridad
        messages.error(request, "No tienes permisos.")
        return redirect("home")             # ← si no es admin, lo saca

    # ... resto de la vista
```

El `@login_required` bloquea a usuarios no logueados antes de entrar.
El `if not es_admin(...)` bloquea a usuarios logueados que no son admin.
Dos capas de seguridad.

---

## ⚙️ Paso 4 — Crear las vistas

### 4.1 Vista de resumen (dashboard_home)

Esta es la primera vista que ves al entrar al dashboard.
Su trabajo es contar datos y mostrarlos:

```python
@login_required
def dashboard_home(request):
    if not es_admin(request.user):
        return redirect("home")

    context = {
        "total_reservas":       Reserva.objects.count(),
        "reservas_pendientes":  Reserva.objects.filter(estado="PENDIENTE").count(),
        "reservas_confirmadas": Reserva.objects.filter(estado="CONFIRMADA").count(),
        "reservas_canceladas":  Reserva.objects.filter(estado__in=["CANCELADA","RECHAZADA"]).count(),
        "total_barberos":       Barbero.objects.filter(disponible=True).count(),
        "total_clientes":       Usuario.objects.filter(rol="CLIENTE").count(),
        "total_servicios":      Servicio.objects.filter(activo=True).count(),
        "ultimas_reservas":     Reserva.objects.select_related(
                                    "cliente", "barbero__user", "servicio"
                                ).order_by("-creado_en")[:10],
    }
    return render(request, "dashboard/home.html", context)
```

**Conceptos clave:**
- `.count()` — no trae los objetos, solo cuenta cuántos hay (más rápido)
- `.filter(estado="PENDIENTE")` — filtra por condición
- `estado__in=[...]` — filtra por múltiples valores a la vez
- `select_related(...)` — trae datos relacionados en una sola consulta SQL
- `.order_by("-creado_en")` — ordena descendente (el `-` es descendente)
- `[:10]` — limita a 10 resultados (como LIMIT 10 en SQL)
- `context` — diccionario que se pasa al template; las claves se convierten en variables en el HTML

---

### 4.2 Vista de lista con filtros (dashboard_reservas)

```python
@login_required
def dashboard_reservas(request):
    if not es_admin(request.user):
        return redirect("home")

    # Empieza con TODAS las reservas
    qs = Reserva.objects.select_related(
        "cliente", "barbero__user", "servicio"
    ).order_by("-creado_en")

    # Lee los filtros de la URL (?estado=PENDIENTE&barbero=2)
    estado_filtro  = request.GET.get("estado", "")
    barbero_filtro = request.GET.get("barbero", "")
    fecha_filtro   = request.GET.get("fecha", "")

    # Aplica cada filtro solo si tiene valor
    if estado_filtro:
        qs = qs.filter(estado=estado_filtro)
    if barbero_filtro:
        qs = qs.filter(barbero_id=barbero_filtro)
    if fecha_filtro:
        qs = qs.filter(fecha=fecha_filtro)

    context = {
        "reservas":       qs,
        "barberos":       Barbero.objects.all(),
        "estado_filtro":  estado_filtro,
        "barbero_filtro": barbero_filtro,
        "fecha_filtro":   fecha_filtro,
    }
    return render(request, "dashboard/reservas_list.html", context)
```

**¿Cómo funcionan los filtros?**

El formulario de filtros en el HTML usa `method="GET"`. Cuando el admin
hace clic en "Filtrar", el navegador agrega los valores a la URL:
`/dashboard/reservas/?estado=PENDIENTE&barbero=2&fecha=2026-05-19`

`request.GET.get("estado", "")` lee ese valor. El segundo argumento `""`
es el valor por defecto si no viene nada.

Los filtros se apilan: si filtras por estado Y barbero, se aplican los dos.

También se mandan de vuelta al template (`estado_filtro`, etc.) para que
el formulario muestre qué filtros están activos.

---

### 4.3 El patrón GET/POST para formularios

Todas las vistas de crear y editar siguen este mismo patrón:

```python
@login_required
def dashboard_reserva_editar(request, reserva_id):
    if not es_admin(request.user):
        return redirect("home")

    # Busca la reserva. Si no existe → error 404 automático
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.method == "POST":
        # ── El admin envió el formulario ──
        reserva.cliente_id  = request.POST.get("cliente")
        reserva.barbero_id  = request.POST.get("barbero")
        reserva.servicio_id = request.POST.get("servicio")
        reserva.fecha       = request.POST.get("fecha")
        reserva.hora        = request.POST.get("hora")
        reserva.estado      = request.POST.get("estado")
        reserva.save()
        messages.success(request, "Reserva actualizada.")
        return redirect("dashboard_reservas")

    # ── El admin entró a la página (GET) ──
    context = {
        "reserva":   reserva,
        "clientes":  Usuario.objects.filter(rol="CLIENTE"),
        "barberos":  Barbero.objects.all(),
        "servicios": Servicio.objects.filter(activo=True),
    }
    return render(request, "dashboard/reserva_form.html", context)
```

**El flujo paso a paso:**

```
Admin hace clic en "Editar" en la tabla
        ↓
Navegador hace GET a /dashboard/reservas/5/editar/
        ↓
Django ejecuta la vista con reserva_id=5
        ↓
get_object_or_404 busca la Reserva con id=5
        ↓
request.method es "GET" → muestra el formulario con los datos actuales
        ↓
Admin modifica los campos y hace clic en "Guardar"
        ↓
Navegador hace POST a la misma URL
        ↓
request.method es "POST" → lee los nuevos valores
        ↓
reserva.save() guarda en la base de datos
        ↓
redirect lleva al admin de vuelta a la lista
```

Para **crear** es igual pero sin el `get_object_or_404` al inicio
(porque el objeto aún no existe) y usando `Modelo.objects.create(...)`.

---

### 4.4 El patrón de eliminación con confirmación

```python
@login_required
def dashboard_reserva_eliminar(request, reserva_id):
    if not es_admin(request.user):
        return redirect("home")

    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.method == "POST":
        reserva.delete()
        messages.success(request, "Reserva eliminada.")
        return redirect("dashboard_reservas")

    # GET → mostrar pantalla de confirmación
    return render(request, "dashboard/confirmar_eliminar.html", {
        "mensaje":      f"¿Eliminar la reserva #{reserva.id}?",
        "cancelar_url": "/dashboard/reservas/",
    })
```

**¿Por qué no eliminar directo con un link?**

Un link siempre hace GET. Si pones un link que elimina directamente,
cualquier bot o crawler que visite tu página podría eliminar datos
sin querer. Por eso la eliminación siempre requiere un POST
(que solo viene de un formulario con botón).

El template `confirmar_eliminar.html` se reutiliza para todo.
Solo cambia el `mensaje` y el `cancelar_url` que le pasas.

---

### 4.5 Caso especial: crear barbero

```python
@login_required
def dashboard_barbero_crear(request):
    if request.method == "POST":

        # Validaciones primero
        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "dashboard/barbero_form.html", {"form_data": request.POST})

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, "Ese usuario ya existe.")
            return render(request, "dashboard/barbero_form.html", {"form_data": request.POST})

        # Paso 1: crear el Usuario
        user = Usuario.objects.create_user(
            username=username,
            password=password1,
            rol="BARBERO",
        )

        # Paso 2: crear el Barbero vinculado
        Barbero.objects.create(
            user=user,
            especialidad=especialidad,
            disponible=disponible
        )
```

**¿Por qué dos pasos?**

El modelo `Barbero` tiene `user = OneToOneField(Usuario)`.
Eso significa que un Barbero NECESITA un Usuario para existir.
Primero creas la cuenta de acceso, luego el perfil de barbero.

Cuando se elimina el barbero, se usa `barbero.user.delete()` en vez de
`barbero.delete()`. Esto elimina el Usuario, y como el Barbero tiene
`on_delete=CASCADE`, se elimina automáticamente también.

---

## 🔗 Paso 5 — Registrar las URLs (urls.py)

Abres `urls.py` y haces dos cosas:

**1. Importar dashboard_views al inicio:**

```python
from . import views
from . import dashboard_views   # ← agregar esta línea
```

**2. Agregar las rutas al final de urlpatterns:**

```python
urlpatterns = [
    # ... las URLs que ya existían ...

    # Dashboard
    path("dashboard/", dashboard_views.dashboard_home, name="dashboard_home"),

    # Reservas del dashboard
    path("dashboard/reservas/",
         dashboard_views.dashboard_reservas,
         name="dashboard_reservas"),

    path("dashboard/reservas/<int:reserva_id>/editar/",
         dashboard_views.dashboard_reserva_editar,
         name="dashboard_reserva_editar"),

    path("dashboard/reservas/<int:reserva_id>/eliminar/",
         dashboard_views.dashboard_reserva_eliminar,
         name="dashboard_reserva_eliminar"),

    # Barberos del dashboard
    path("dashboard/barberos/",
         dashboard_views.dashboard_barberos,
         name="dashboard_barberos"),

    path("dashboard/barberos/crear/",
         dashboard_views.dashboard_barbero_crear,
         name="dashboard_barbero_crear"),

    path("dashboard/barberos/<int:barbero_id>/editar/",
         dashboard_views.dashboard_barbero_editar,
         name="dashboard_barbero_editar"),

    path("dashboard/barberos/<int:barbero_id>/eliminar/",
         dashboard_views.dashboard_barbero_eliminar,
         name="dashboard_barbero_eliminar"),

    # ... igual para servicios y usuarios
]
```

**¿Por qué los nombres (`name="..."`) son importantes?**

En los templates usas `{% url 'dashboard_reservas' %}` en vez de
escribir la URL a mano. Si mañana cambias la URL de `/dashboard/reservas/`
a `/admin/reservas/`, solo cambias el `path(...)` y todos los links
del proyecto se actualizan solos.

---

## 🏗️ Paso 6 — Crear el layout base del dashboard

Crea el archivo `templates/layouts/dashboard_base.html`.

**¿Por qué un base separado del base.html del sitio?**

El sitio público tiene: navbar → contenido → footer (vertical).
El dashboard tiene: navbar → sidebar + contenido (horizontal con flexbox).
Son estructuras diferentes, necesitan bases diferentes.

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
  <title>{% block title %}Dashboard{% endblock %} — Admin</title>

  <!-- CSS base del proyecto -->
  <link rel="stylesheet" href="{% static 'css/base.css' %}">
  <!-- CSS compartido de TODO el dashboard -->
  <link rel="stylesheet" href="{% static 'css/dashboard/dashboard.css' %}">
  <!-- CSS específico de cada página (cada template lo define) -->
  {% block extra_css %}{% endblock %}
</head>
<body>

  <!-- Navbar superior -->
  <nav class="navbar">
    <div class="logo">✂ BarberShop <span class="navbar-subtitle">/ Admin</span></div>
    <div class="nav-links">
      <a href="{% url 'home' %}">← Ver sitio</a>
      <a class="logout" href="{% url 'logout' %}">Salir</a>
    </div>
  </nav>

  <!-- Contenedor principal: sidebar + contenido -->
  <div class="dashboard-wrapper">

    <!-- Sidebar izquierdo -->
    <aside class="dashboard-sidebar">
      <div class="sidebar-title">Panel de Control</div>
      <nav class="sidebar-nav">

        <!-- El link activo se detecta comparando la URL actual -->
        <a href="{% url 'dashboard_home' %}"
           class="{% if request.resolver_match.url_name == 'dashboard_home' %}active{% endif %}">
          <span class="sidebar-icon">📊</span> Resumen
        </a>

        <hr class="sidebar-divider">

        <a href="{% url 'dashboard_reservas' %}"
           class="{% if 'dashboard_reserva' in request.resolver_match.url_name %}active{% endif %}">
          <span class="sidebar-icon">📅</span> Reservas
        </a>

        <!-- ... resto de links -->
      </nav>
    </aside>

    <!-- Contenido principal (cada template llena este bloque) -->
    <main class="dashboard-content">
      {% if messages %}
        <div class="messages">
          {% for message in messages %}
            <div class="message {{ message.tags }}">{{ message }}</div>
          {% endfor %}
        </div>
      {% endif %}

      {% block content %}{% endblock %}
    </main>

  </div>
</body>
</html>
```

**¿Cómo detecta el link activo en el sidebar?**

`request.resolver_match.url_name` contiene el nombre de la URL actual.
Por ejemplo, si estás en `/dashboard/reservas/5/editar/`, su valor es
`"dashboard_reserva_editar"`.

```html
class="{% if 'dashboard_reserva' in request.resolver_match.url_name %}active{% endif %}"
```

Esto verifica si el texto `"dashboard_reserva"` está DENTRO del nombre.
Así, tanto `dashboard_reservas` como `dashboard_reserva_editar` y
`dashboard_reserva_eliminar` activan el mismo link del sidebar.

---

## 📄 Paso 7 — Crear los templates HTML

Cada template empieza igual:

```html
{% extends 'layouts/dashboard_base.html' %}
{% load static %}

{% block title %}Reservas{% endblock %}

{% block extra_css %}
  <link rel="stylesheet" href="{% static 'css/dashboard/reservas_list.css' %}">
{% endblock %}

{% block content %}
  <!-- aquí va el contenido de la página -->
{% endblock %}
```

- `{% extends %}` — hereda toda la estructura del base (navbar, sidebar, etc.)
- `{% load static %}` — necesario para usar `{% static '...' %}`
- `{% block title %}` — define el título de la pestaña del navegador
- `{% block extra_css %}` — carga el CSS específico de esta página
- `{% block content %}` — aquí va el HTML único de esta página

**Template de lista (tabla):**

```html
{% block content %}
<div class="dashboard-header">
  <h1>📅 Gestión de Reservas</h1>
</div>

<div class="dash-table-wrapper">
  <div class="dash-table-header">
    <h2>Reservas ({{ reservas.count }})</h2>
  </div>
  <table class="dash-table">
    <thead>
      <tr><th>#</th><th>Cliente</th><th>Estado</th><th>Acciones</th></tr>
    </thead>
    <tbody>
      {% for r in reservas %}
        <tr>
          <td>{{ r.id }}</td>
          <td>{{ r.cliente.username }}</td>
          <td><span class="badge badge-{{ r.estado|lower }}">{{ r.get_estado_display }}</span></td>
          <td>
            <a href="{% url 'dashboard_reserva_editar' r.id %}" class="btn-dash btn-secondary btn-sm">✏ Editar</a>
            <a href="{% url 'dashboard_reserva_eliminar' r.id %}" class="btn-dash btn-danger btn-sm">🗑</a>
          </td>
        </tr>
      {% empty %}
        <tr class="empty-row"><td colspan="4">No hay reservas.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
```

**Cosas importantes del template:**
- `{{ reservas.count }}` — llama al método count del queryset
- `{% for r in reservas %}` — itera sobre cada reserva
- `r.estado|lower` — el filtro `lower` convierte a minúsculas (PENDIENTE → pendiente)
  para que coincida con la clase CSS `badge-pendiente`
- `r.get_estado_display` — método de Django que devuelve el texto legible del choice
- `{% url 'dashboard_reserva_editar' r.id %}` — genera la URL con el id dinámico
- `{% empty %}` — se muestra si el queryset está vacío

---

## 🎨 Paso 8 — Crear los CSS

### Estructura de carpetas

```
static/css/
├── base.css              ← ya existía, estilos del sitio público
└── dashboard/            ← carpeta nueva para el dashboard
    ├── dashboard.css     ← estilos compartidos de TODO el dashboard
    ├── home.css          ← solo para home.html
    ├── reservas_list.css ← solo para reservas_list.html
    └── ...
```

### dashboard.css — El archivo más importante

Este archivo lo carga `dashboard_base.html` en TODAS las páginas.
Contiene los estilos que se repiten en todo el dashboard:

```css
/* Layout principal */
.dashboard-wrapper { display: flex; min-height: calc(100vh - 60px); }

/* Sidebar */
.dashboard-sidebar { width: 240px; background: #1c1c1c; }
.sidebar-nav a { display: flex; padding: 11px 20px; color: #ccc; }
.sidebar-nav a.active { color: #c59d5f; border-left: 3px solid #c59d5f; }

/* Tablas */
.dash-table { width: 100%; border-collapse: collapse; }
.dash-table thead th { background: #161616; color: #888; }
.dash-table tbody tr:hover { background: #222; }

/* Badges de estado */
.badge { padding: 3px 10px; border-radius: 20px; font-size: 11px; }
.badge-pendiente  { background: #3a3010; color: #f0c040; }
.badge-confirmada { background: #0f2e1a; color: #4caf82; }

/* Botones */
.btn-dash { display: inline-flex; padding: 8px 16px; border-radius: 8px; }
.btn-primary   { background: #c59d5f; color: #111; }
.btn-danger    { background: #7a2020; color: #ffd1d1; }
.btn-secondary { background: #2a2a2a; color: #ccc; }
```

### CSS individuales

Cada template carga su propio CSS para estilos únicos de esa página.
Si una página no tiene estilos únicos, el archivo puede estar vacío
o con solo un comentario.

---

## 🔗 Paso 9 — Conectar el link en el navbar

Abre `templates/layouts/base.html` y busca el bloque de navegación.
Reemplaza el link al admin de Django por el link a tu dashboard:

**Antes (admin de Django):**
```html
{% if user.is_authenticated and user.is_staff %}
  <a href="{% url 'admin:index' %}">Dashboard</a>
{% endif %}
```

**Después (tu dashboard):**
```html
{% if user.is_superuser or user.rol == "ADMIN" %}
  <a href="{% url 'dashboard_home' %}">Dashboard</a>
{% endif %}
```

**¿Por qué cambiar la condición?**

`user.is_staff` es una propiedad de Django que no tiene relación con
tu campo `rol`. Tu sistema usa `rol == "ADMIN"` para definir quién
es administrador, así que esa es la condición correcta.

---

## ✅ Paso 10 — Probar todo

Sigue este orden para probar:

```
1. python manage.py runserver
2. Entra a http://127.0.0.1:8000/
3. Haz login con un usuario ADMIN o superusuario
4. Verifica que aparece el link "Dashboard" en el navbar
5. Entra al dashboard → debe mostrar el resumen con estadísticas
6. Prueba cada sección del sidebar
7. Prueba crear un barbero nuevo
8. Prueba editar una reserva
9. Prueba eliminar un servicio (verifica que aparece la confirmación)
10. Prueba los filtros en la lista de reservas
11. Intenta entrar al dashboard con un usuario CLIENTE → debe redirigir al inicio
```

---

## 🚨 Errores comunes y cómo resolverlos

| Error | Causa | Solución |
|-------|-------|----------|
| `TemplateDoesNotExist: dashboard/home.html` | El template no existe o está en la carpeta equivocada | Verifica que el archivo esté en `templates/dashboard/home.html` dentro de la app |
| `ImportError: cannot import name 'dashboard_views'` | El archivo `dashboard_views.py` no existe | Crea el archivo en la misma carpeta que `views.py` |
| `NoReverseMatch: 'dashboard_home'` | La URL no está registrada | Verifica que agregaste el `path(...)` en `urls.py` y que importaste `dashboard_views` |
| CSS no carga (404) | `STATICFILES_DIRS` mal configurado | Verifica en `settings.py` que apunta a la carpeta `static` de tu app |
| Sidebar sin estilos | `dashboard.css` no se carga | Verifica que `dashboard_base.html` tiene el `{% load static %}` al inicio |

---

## 📌 Resumen del orden correcto

```
1. dashboard_views.py  → primero la lógica (sin esto nada funciona)
2. urls.py             → segundo las rutas (conecta URLs con vistas)
3. dashboard_base.html → tercero el layout (base de todos los templates)
4. templates/dashboard/→ cuarto los templates (lo que ve el usuario)
5. static/css/dashboard/→ quinto los estilos (el diseño visual)
6. base.html           → último conectar el navbar del sitio público
```

Este orden importa porque cada paso depende del anterior.
No puedes crear el template si no tienes el base.
No puedes probar la vista si no tienes la URL registrada.
