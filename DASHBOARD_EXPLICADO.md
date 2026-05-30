# 📊 Cómo se construyó el Dashboard — Explicación completa

---

## 🗂️ Archivos que se crearon o modificaron

Para agregar el dashboard al proyecto que ya existía, se tocaron estos archivos:

### Archivos CREADOS (nuevos)
```
reservaciones_barberia/
├── dashboard_views.py                          ← toda la lógica del dashboard
├── static/css/dashboard/
│   ├── dashboard.css                           ← estilos compartidos de todo el dashboard
│   ├── home.css                                ← estilos extra para el resumen
│   ├── reservas_list.css                       ← estilos extra para lista de reservas
│   ├── reserva_form.css                        ← estilos extra para formulario de reserva
│   ├── barberos_list.css                       ← estilos extra para lista de barberos
│   ├── barbero_form.css                        ← estilos extra para formulario de barbero
│   ├── servicios_list.css                      ← estilos extra para lista de servicios
│   ├── servicio_form.css                       ← estilos extra para formulario de servicio
│   ├── usuarios_list.css                       ← estilos extra para lista de usuarios
│   ├── usuario_form.css                        ← estilos extra para formulario de usuario
│   └── confirmar_eliminar.css                  ← estilos extra para confirmación
└── templates/
    ├── layouts/dashboard_base.html             ← plantilla base del dashboard
    └── dashboard/
        ├── home.html                           ← página de resumen
        ├── reservas_list.html                  ← lista de reservas
        ├── reserva_form.html                   ← formulario crear/editar reserva
        ├── barberos_list.html                  ← lista de barberos
        ├── barbero_form.html                   ← formulario crear/editar barbero
        ├── servicios_list.html                 ← lista de servicios
        ├── servicio_form.html                  ← formulario crear/editar servicio
        ├── usuarios_list.html                  ← lista de usuarios
        ├── usuario_form.html                   ← formulario crear/editar usuario
        └── confirmar_eliminar.html             ← pantalla de confirmación al eliminar
```

### Archivos MODIFICADOS (ya existían)
```
reservaciones_barberia/urls.py     ← se agregaron todas las URLs del dashboard
pagina_reservaciones/settings.py   ← se corrigió STATICFILES_DIRS y TEMPLATES
templates/layouts/base.html        ← se agregó el link "Dashboard" en el navbar
```

---

## 🔌 Paso 1 — Conectar las URLs (urls.py)

El primer paso fue registrar todas las rutas del dashboard en `urls.py`.
Sin esto, Django no sabe que `/dashboard/` existe.

Se importó `dashboard_views` y se agregaron las rutas al final del archivo:

```python
from . import dashboard_views

urlpatterns = [
    # ... las URLs que ya existían ...

    # Dashboard
    path("dashboard/", dashboard_views.dashboard_home, name="dashboard_home"),

    path("dashboard/reservas/", dashboard_views.dashboard_reservas, name="dashboard_reservas"),
    path("dashboard/reservas/<int:reserva_id>/editar/", dashboard_views.dashboard_reserva_editar, name="dashboard_reserva_editar"),
    path("dashboard/reservas/<int:reserva_id>/eliminar/", dashboard_views.dashboard_reserva_eliminar, name="dashboard_reserva_eliminar"),

    path("dashboard/barberos/", dashboard_views.dashboard_barberos, name="dashboard_barberos"),
    path("dashboard/barberos/crear/", dashboard_views.dashboard_barbero_crear, name="dashboard_barbero_crear"),
    path("dashboard/barberos/<int:barbero_id>/editar/", dashboard_views.dashboard_barbero_editar, name="dashboard_barbero_editar"),
    path("dashboard/barberos/<int:barbero_id>/eliminar/", dashboard_views.dashboard_barbero_eliminar, name="dashboard_barbero_eliminar"),

    # ... igual para servicios y usuarios
]
```

**¿Cómo funciona `<int:reserva_id>`?**
Es un parámetro dinámico. Cuando alguien entra a `/dashboard/reservas/5/editar/`,
Django captura el `5` y se lo pasa a la vista como `reserva_id=5`.

---

## 🧠 Paso 2 — La lógica (dashboard_views.py)

Este archivo contiene todas las funciones del dashboard.
Se creó separado de `views.py` para mantener el código organizado.

### La función de seguridad: `es_admin()`

```python
def es_admin(user):
    return user.is_authenticated and (user.is_superuser or user.rol == "ADMIN")
```

Esta función se llama al inicio de CADA vista del dashboard.
Verifica dos cosas:
1. Que el usuario esté logueado (`is_authenticated`)
2. Que sea superusuario O tenga rol ADMIN

Si no cumple, lo manda al inicio. Así nadie puede entrar al dashboard
escribiendo la URL directamente.

---

### 📊 `dashboard_home` — El resumen

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

**¿Qué hace cada línea?**
- `Reserva.objects.count()` — cuenta TODAS las reservas en la base de datos
- `.filter(estado="PENDIENTE").count()` — cuenta solo las pendientes
- `estado__in=["CANCELADA","RECHAZADA"]` — cuenta las que tienen cualquiera de esos dos estados
- `select_related(...)` — trae los datos relacionados (cliente, barbero, servicio) en una sola consulta a la BD, más eficiente
- `.order_by("-creado_en")` — ordena de más reciente a más antigua (el `-` significa descendente)
- `[:10]` — toma solo los primeros 10 resultados

Todo esto se manda al template en el diccionario `context`.

---

### 📅 `dashboard_reservas` — Lista con filtros

```python
@login_required
def dashboard_reservas(request):
    if not es_admin(request.user):
        return redirect("home")

    qs = Reserva.objects.select_related("cliente", "barbero__user", "servicio").order_by("-creado_en")

    estado_filtro  = request.GET.get("estado", "")
    barbero_filtro = request.GET.get("barbero", "")
    fecha_filtro   = request.GET.get("fecha", "")

    if estado_filtro:
        qs = qs.filter(estado=estado_filtro)
    if barbero_filtro:
        qs = qs.filter(barbero_id=barbero_filtro)
    if fecha_filtro:
        qs = qs.filter(fecha=fecha_filtro)

    return render(request, "dashboard/reservas_list.html", {"reservas": qs, ...})
```

**¿Cómo funcionan los filtros?**

Cuando el admin usa el formulario de filtros, el navegador envía los valores
en la URL así: `/dashboard/reservas/?estado=PENDIENTE&barbero=2`

`request.GET.get("estado", "")` lee ese valor de la URL.
Si viene vacío, no aplica ese filtro. Si viene con valor, agrega un `.filter()` al queryset.

Los filtros se van apilando: primero filtra por estado, luego por barbero, luego por fecha.
Así puedes combinar varios filtros a la vez.

---

### ✏️ Patrón GET/POST — Editar y Crear

Todas las vistas de formulario (crear/editar) siguen el mismo patrón:

```python
@login_required
def dashboard_reserva_editar(request, reserva_id):
    if not es_admin(request.user):
        return redirect("home")

    reserva = get_object_or_404(Reserva, id=reserva_id)  # busca o devuelve 404

    if request.method == "POST":
        # El admin envió el formulario → guardar cambios
        reserva.cliente_id  = request.POST.get("cliente")
        reserva.barbero_id  = request.POST.get("barbero")
        reserva.servicio_id = request.POST.get("servicio")
        reserva.fecha       = request.POST.get("fecha")
        reserva.hora        = request.POST.get("hora")
        reserva.estado      = request.POST.get("estado")
        reserva.save()
        messages.success(request, "Reserva actualizada correctamente.")
        return redirect("dashboard_reservas")

    # Si es GET → mostrar el formulario con los datos actuales
    context = {
        "reserva":   reserva,
        "clientes":  Usuario.objects.filter(rol="CLIENTE"),
        "barberos":  Barbero.objects.all(),
        "servicios": Servicio.objects.filter(activo=True),
    }
    return render(request, "dashboard/reserva_form.html", context)
```

**El flujo es:**
1. Admin entra a la URL → Django ejecuta la vista con GET
2. La vista busca la reserva en la BD con `get_object_or_404`
3. Manda los datos al template → el formulario aparece con los valores actuales
4. Admin modifica y hace clic en "Guardar" → el navegador envía POST
5. La vista lee los nuevos valores con `request.POST.get(...)`
6. Guarda con `.save()` y redirige a la lista

`get_object_or_404` es una función de Django que busca el objeto.
Si no existe (por ejemplo, alguien escribe `/dashboard/reservas/999/editar/`
y no hay reserva con id 999), devuelve automáticamente una página de error 404.

---

### 🗑️ Patrón de eliminación con confirmación

```python
@login_required
def dashboard_reserva_eliminar(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.method == "POST":
        reserva.delete()                          # elimina de la BD
        messages.success(request, "Reserva eliminada.")
        return redirect("dashboard_reservas")

    # Si es GET → mostrar pantalla de confirmación
    return render(request, "dashboard/confirmar_eliminar.html", {
        "mensaje":      f"¿Eliminar la reserva #{reserva.id}?",
        "cancelar_url": "/dashboard/reservas/",
    })
```

**¿Por qué hay una pantalla de confirmación?**

Para evitar eliminar algo por accidente. El flujo es:
1. Admin hace clic en 🗑 → GET → aparece "¿Estás seguro?"
2. Admin hace clic en "Sí, eliminar" → POST → se elimina
3. Admin hace clic en "Cancelar" → vuelve a la lista sin eliminar nada

El mismo template `confirmar_eliminar.html` se reutiliza para barberos,
servicios y usuarios. Solo cambia el `mensaje` y el `cancelar_url`.

---

### 💈 `dashboard_barbero_crear` — Crear barbero (caso especial)

```python
@login_required
def dashboard_barbero_crear(request):
    if request.method == "POST":
        # Primero crear el Usuario
        user = Usuario.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            rol="BARBERO",          # ← rol obligatorio
        )
        # Luego crear el Barbero vinculado a ese usuario
        Barbero.objects.create(
            user=user,
            especialidad=especialidad,
            disponible=disponible
        )
```

**¿Por qué se crean dos objetos?**

Porque en el modelo, `Barbero` no es un usuario por sí solo.
Es un perfil extra que se conecta a un `Usuario` existente.
Entonces primero se crea la cuenta de acceso (Usuario) y luego
el perfil de barbero (Barbero) que apunta a esa cuenta.

Si el admin elimina un barbero, también se elimina su cuenta de usuario
porque en el modelo está definido `on_delete=models.CASCADE`.

---

### ⏸️ `dashboard_servicio_toggle` — Activar/Desactivar

```python
@login_required
def dashboard_servicio_toggle(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)
    servicio.activo = not servicio.activo   # invierte el valor: True→False, False→True
    servicio.save()
    return redirect("dashboard_servicios")
```

Esta es la función más simple del dashboard.
`not servicio.activo` invierte el booleano: si estaba activo lo desactiva,
si estaba inactivo lo activa. Con un solo clic, sin formulario.

---

### 👤 `dashboard_usuario_eliminar` — Protección especial

```python
@login_required
def dashboard_usuario_eliminar(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.user == usuario:
        messages.error(request, "No puedes eliminar tu propia cuenta.")
        return redirect("dashboard_usuarios")

    if request.method == "POST":
        usuario.delete()
        return redirect("dashboard_usuarios")
```

Tiene una verificación extra: `request.user == usuario`.
Compara si el usuario logueado es el mismo que se quiere eliminar.
Si es así, lo bloquea. Esto evita que el admin se elimine a sí mismo
y quede el sistema sin administrador.

---

## 🎨 Paso 3 — El layout base del dashboard (dashboard_base.html)

Se creó una plantilla base separada de `base.html` porque el dashboard
tiene una estructura diferente: sidebar + contenido, en vez de navbar + contenido.

```html
{% load static %}
<head>
  <link rel="stylesheet" href="{% static 'css/base.css' %}">
  <link rel="stylesheet" href="{% static 'css/dashboard/dashboard.css' %}">
  {% block extra_css %}{% endblock %}   ← cada página carga su CSS extra aquí
</head>

<body>
  <nav class="navbar">...</nav>

  <div class="dashboard-wrapper">        ← flex container
    <aside class="dashboard-sidebar">    ← sidebar izquierdo
      <nav class="sidebar-nav">
        <a href="{% url 'dashboard_home' %}">📊 Resumen</a>
        <a href="{% url 'dashboard_reservas' %}">📅 Reservas</a>
        ...
      </nav>
    </aside>

    <main class="dashboard-content">     ← contenido derecho
      {% block content %}{% endblock %}  ← aquí va el contenido de cada página
    </main>
  </div>
</body>
```

**¿Cómo sabe el sidebar qué link está activo?**

```html
<a href="{% url 'dashboard_reservas' %}"
   class="{% if 'dashboard_reserva' in request.resolver_match.url_name %}active{% endif %}">
```

`request.resolver_match.url_name` es el nombre de la URL actual.
Si contiene `"dashboard_reserva"`, agrega la clase `active` que pinta
el link de dorado en el CSS.

---

## 🎨 Paso 4 — Los CSS del dashboard

Se organizaron en dos niveles:

### `dashboard.css` — Estilos compartidos
Cargado en `dashboard_base.html`, disponible en TODAS las páginas del dashboard.
Contiene: layout, sidebar, tablas, badges, botones, formularios, confirm.

### CSS individuales — Estilos específicos
Cada template carga su propio CSS extra via `{% block extra_css %}`:

```html
{% block extra_css %}
  <link rel="stylesheet" href="{% static 'css/dashboard/home.css' %}">
{% endblock %}
```

Así `home.css` solo se carga en la página de resumen,
`reservas_list.css` solo en la lista de reservas, etc.
Esto hace que el navegador no cargue CSS innecesario en cada página.

---

## 🔗 Paso 5 — Conectar el navbar del sitio público

Se modificó `layouts/base.html` para que los admins vean el link al dashboard:

```html
{% if user.is_superuser or user.rol == "ADMIN" %}
  <a href="{% url 'clientes' %}">Clientes</a>
  <a href="{% url 'dashboard_home' %}">Dashboard</a>
{% endif %}
```

Solo aparece si el usuario tiene rol ADMIN o es superusuario.
Los clientes y barberos no lo ven.

---

## 📋 Resumen de todas las funciones del dashboard

| Función | Qué hace |
|---------|----------|
| `es_admin(user)` | Verifica si el usuario puede entrar al dashboard |
| `dashboard_home` | Muestra estadísticas y últimas 10 reservas |
| `dashboard_reservas` | Lista todas las reservas con filtros por estado/barbero/fecha |
| `dashboard_reserva_editar` | Formulario para editar una reserva existente |
| `dashboard_reserva_eliminar` | Confirmación y eliminación de una reserva |
| `dashboard_barberos` | Lista todos los barberos |
| `dashboard_barbero_crear` | Crea un Usuario con rol BARBERO y su perfil Barbero |
| `dashboard_barbero_editar` | Edita datos del usuario y del barbero |
| `dashboard_barbero_eliminar` | Elimina el barbero y su cuenta de usuario |
| `dashboard_servicios` | Lista todos los servicios |
| `dashboard_servicio_crear` | Crea un nuevo servicio |
| `dashboard_servicio_editar` | Edita un servicio existente |
| `dashboard_servicio_toggle` | Activa o desactiva un servicio con un clic |
| `dashboard_servicio_eliminar` | Elimina un servicio |
| `dashboard_usuarios` | Lista todos los usuarios del sistema |
| `dashboard_usuario_crear` | Crea un nuevo usuario con cualquier rol |
| `dashboard_usuario_editar` | Edita datos del usuario (incluyendo cambio de contraseña) |
| `dashboard_usuario_eliminar` | Elimina un usuario (con protección para no eliminarse a sí mismo) |

---

## 🔄 Flujo completo cuando el admin entra al dashboard

```
1. Admin entra a /dashboard/
2. Django ejecuta dashboard_home()
3. es_admin() verifica que sea ADMIN → pasa
4. Se hacen 7 consultas a la BD (conteos + últimas reservas)
5. Los datos se mandan al template dashboard/home.html
6. El template extiende layouts/dashboard_base.html
7. dashboard_base.html carga base.css + dashboard.css
8. home.html carga home.css via {% block extra_css %}
9. El navegador muestra el dashboard con sidebar y tarjetas de estadísticas

Si el admin hace clic en "Reservas":
10. Navega a /dashboard/reservas/
11. Django ejecuta dashboard_reservas()
12. Trae todas las reservas ordenadas por fecha
13. Muestra reservas_list.html con la tabla y los filtros

Si el admin filtra por estado "PENDIENTE":
14. El formulario envía GET a /dashboard/reservas/?estado=PENDIENTE
15. Django ejecuta dashboard_reservas() de nuevo
16. request.GET.get("estado") devuelve "PENDIENTE"
17. Se aplica .filter(estado="PENDIENTE") al queryset
18. La tabla muestra solo las reservas pendientes
```
