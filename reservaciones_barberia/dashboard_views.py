from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Barbero, Servicio, Reserva, Usuario


def es_admin(user):
    return user.is_authenticated and (user.is_superuser or user.rol == "ADMIN")


# ─────────────────────────────────────────
# HOME / RESUMEN
# ─────────────────────────────────────────
@login_required
def dashboard_home(request):
    if not es_admin(request.user):
        messages.error(request, "No tienes permisos para acceder al dashboard.")
        return redirect("home")

    context = {
        "total_reservas":       Reserva.objects.count(),
        "reservas_pendientes":  Reserva.objects.filter(estado="PENDIENTE").count(),
        "reservas_confirmadas": Reserva.objects.filter(estado="CONFIRMADA").count(),
        "reservas_canceladas":  Reserva.objects.filter(estado__in=["CANCELADA", "RECHAZADA"]).count(),
        "total_barberos":       Barbero.objects.filter(disponible=True).count(),
        "total_clientes":       Usuario.objects.filter(rol="CLIENTE").count(),
        "total_servicios":      Servicio.objects.filter(activo=True).count(),
        "ultimas_reservas":     Reserva.objects.select_related(
                                    "cliente", "barbero__user", "servicio"
                                ).order_by("-creado_en")[:10],
    }
    return render(request, "dashboard/home.html", context)


# ─────────────────────────────────────────
# RESERVAS
# ─────────────────────────────────────────
@login_required
def dashboard_reservas(request):
    if not es_admin(request.user):
        return redirect("home")

    qs = Reserva.objects.select_related(
        "cliente", "barbero__user", "servicio"
    ).order_by("-creado_en")

    estado_filtro  = request.GET.get("estado", "")
    barbero_filtro = request.GET.get("barbero", "")
    fecha_filtro   = request.GET.get("fecha", "")

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


@login_required
def dashboard_reserva_editar(request, reserva_id):
    if not es_admin(request.user):
        return redirect("home")

    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.method == "POST":
        reserva.cliente_id  = request.POST.get("cliente")
        reserva.barbero_id  = request.POST.get("barbero")
        reserva.servicio_id = request.POST.get("servicio")
        reserva.fecha       = request.POST.get("fecha")
        reserva.hora        = request.POST.get("hora")
        reserva.estado      = request.POST.get("estado")
        reserva.save()
        messages.success(request, "Reserva actualizada correctamente.")
        return redirect("dashboard_reservas")

    context = {
        "reserva":   reserva,
        "clientes":  Usuario.objects.filter(rol="CLIENTE"),
        "barberos":  Barbero.objects.all(),
        "servicios": Servicio.objects.filter(activo=True),
    }
    return render(request, "dashboard/reserva_form.html", context)


@login_required
def dashboard_reserva_eliminar(request, reserva_id):
    if not es_admin(request.user):
        return redirect("home")

    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.method == "POST":
        reserva.delete()
        messages.success(request, "Reserva eliminada.")
        return redirect("dashboard_reservas")

    return render(request, "dashboard/confirmar_eliminar.html", {
        "mensaje":      f"¿Eliminar la reserva #{reserva.id} de {reserva.cliente.username}?",
        "cancelar_url": "/dashboard/reservas/",
    })


# ─────────────────────────────────────────
# BARBEROS
# ─────────────────────────────────────────
@login_required
def dashboard_barberos(request):
    if not es_admin(request.user):
        return redirect("home")

    barberos = Barbero.objects.select_related("user").all()
    return render(request, "dashboard/barberos_list.html", {"barberos": barberos})


@login_required
def dashboard_barbero_crear(request):
    if not es_admin(request.user):
        return redirect("home")

    if request.method == "POST":
        username     = request.POST.get("username")
        first_name   = request.POST.get("first_name", "")
        last_name    = request.POST.get("last_name", "")
        email        = request.POST.get("email", "")
        password1    = request.POST.get("password1")
        password2    = request.POST.get("password2")
        especialidad = request.POST.get("especialidad", "")
        disponible   = request.POST.get("disponible") == "on"

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "dashboard/barbero_form.html", {"form_data": request.POST})

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, "Ese nombre de usuario ya existe.")
            return render(request, "dashboard/barbero_form.html", {"form_data": request.POST})

        user = Usuario.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            rol="BARBERO",
        )
        barbero = Barbero.objects.create(user=user, especialidad=especialidad, disponible=disponible)

        # Guardar foto si se subió
        if request.FILES.get("foto"):
            barbero.foto = request.FILES["foto"]
            barbero.save()

        messages.success(request, f"Barbero {username} creado correctamente.")
        return redirect("dashboard_barberos")

    return render(request, "dashboard/barbero_form.html", {})


@login_required
def dashboard_barbero_editar(request, barbero_id):
    if not es_admin(request.user):
        return redirect("home")

    barbero = get_object_or_404(Barbero, id=barbero_id)

    if request.method == "POST":
        barbero.user.first_name = request.POST.get("first_name", "")
        barbero.user.last_name  = request.POST.get("last_name", "")
        barbero.user.email      = request.POST.get("email", "")
        telefono = request.POST.get("telefono", "")
        if telefono:
            barbero.user.telefono = telefono
        barbero.user.save()

        barbero.especialidad = request.POST.get("especialidad", "")
        barbero.disponible   = request.POST.get("disponible") == "on"

        # Actualizar foto si se subió una nueva
        if request.FILES.get("foto"):
            barbero.foto = request.FILES["foto"]

        # Eliminar foto si el admin marcó "eliminar foto"
        if request.POST.get("eliminar_foto") and barbero.foto:
            barbero.foto.delete(save=False)
            barbero.foto = None

        barbero.save()
        messages.success(request, "Barbero actualizado correctamente.")
        return redirect("dashboard_barberos")

    return render(request, "dashboard/barbero_form.html", {"barbero": barbero})


@login_required
def dashboard_barbero_eliminar(request, barbero_id):
    if not es_admin(request.user):
        return redirect("home")

    barbero = get_object_or_404(Barbero, id=barbero_id)

    if request.method == "POST":
        barbero.user.delete()
        messages.success(request, "Barbero eliminado.")
        return redirect("dashboard_barberos")

    return render(request, "dashboard/confirmar_eliminar.html", {
        "mensaje":      f"¿Eliminar al barbero {barbero}? También se eliminará su cuenta de usuario.",
        "cancelar_url": "/dashboard/barberos/",
    })


# ─────────────────────────────────────────
# SERVICIOS
# ─────────────────────────────────────────
@login_required
def dashboard_servicios(request):
    if not es_admin(request.user):
        return redirect("home")

    servicios = Servicio.objects.all()
    return render(request, "dashboard/servicios_list.html", {"servicios": servicios})


@login_required
def dashboard_servicio_crear(request):
    if not es_admin(request.user):
        return redirect("home")

    if request.method == "POST":
        nombre           = request.POST.get("nombre")
        precio           = request.POST.get("precio")
        duracion_minutos = request.POST.get("duracion_minutos")
        activo           = request.POST.get("activo") == "on"

        Servicio.objects.create(
            nombre=nombre,
            precio=precio,
            duracion_minutos=duracion_minutos,
            activo=activo,
        )
        messages.success(request, f"Servicio '{nombre}' creado correctamente.")
        return redirect("dashboard_servicios")

    return render(request, "dashboard/servicio_form.html", {})


@login_required
def dashboard_servicio_editar(request, servicio_id):
    if not es_admin(request.user):
        return redirect("home")

    servicio = get_object_or_404(Servicio, id=servicio_id)

    if request.method == "POST":
        servicio.nombre           = request.POST.get("nombre")
        servicio.precio           = request.POST.get("precio")
        servicio.duracion_minutos = request.POST.get("duracion_minutos")
        servicio.activo           = request.POST.get("activo") == "on"
        servicio.save()
        messages.success(request, "Servicio actualizado correctamente.")
        return redirect("dashboard_servicios")

    return render(request, "dashboard/servicio_form.html", {"servicio": servicio})


@login_required
def dashboard_servicio_toggle(request, servicio_id):
    if not es_admin(request.user):
        return redirect("home")

    servicio = get_object_or_404(Servicio, id=servicio_id)
    servicio.activo = not servicio.activo
    servicio.save()
    estado = "activado" if servicio.activo else "desactivado"
    messages.success(request, f"Servicio '{servicio.nombre}' {estado}.")
    return redirect("dashboard_servicios")


@login_required
def dashboard_servicio_eliminar(request, servicio_id):
    if not es_admin(request.user):
        return redirect("home")

    servicio = get_object_or_404(Servicio, id=servicio_id)

    if request.method == "POST":
        servicio.delete()
        messages.success(request, "Servicio eliminado.")
        return redirect("dashboard_servicios")

    return render(request, "dashboard/confirmar_eliminar.html", {
        "mensaje":      f"¿Eliminar el servicio '{servicio.nombre}'?",
        "cancelar_url": "/dashboard/servicios/",
    })


# ─────────────────────────────────────────
# USUARIOS
# ─────────────────────────────────────────
@login_required
def dashboard_usuarios(request):
    if not es_admin(request.user):
        return redirect("home")

    usuarios = Usuario.objects.all().order_by("username")
    return render(request, "dashboard/usuarios_list.html", {"usuarios": usuarios})


@login_required
def dashboard_usuario_crear(request):
    if not es_admin(request.user):
        return redirect("home")

    if request.method == "POST":
        username   = request.POST.get("username")
        first_name = request.POST.get("first_name", "")
        last_name  = request.POST.get("last_name", "")
        email      = request.POST.get("email", "")
        telefono   = request.POST.get("telefono", "")
        direccion  = request.POST.get("direccion", "")
        rol        = request.POST.get("rol", "CLIENTE")
        password1  = request.POST.get("password1")
        password2  = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "dashboard/usuario_form.html", {"form_data": request.POST})

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, "Ese nombre de usuario ya existe.")
            return render(request, "dashboard/usuario_form.html", {"form_data": request.POST})

        Usuario.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            telefono=telefono,
            direccion=direccion,
            rol=rol,
        )
        messages.success(request, f"Usuario {username} creado correctamente.")
        return redirect("dashboard_usuarios")

    return render(request, "dashboard/usuario_form.html", {})


@login_required
def dashboard_usuario_editar(request, usuario_id):
    if not es_admin(request.user):
        return redirect("home")

    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == "POST":
        usuario.first_name = request.POST.get("first_name", "")
        usuario.last_name  = request.POST.get("last_name", "")
        usuario.email      = request.POST.get("email", "")
        usuario.telefono   = request.POST.get("telefono", "")
        usuario.direccion  = request.POST.get("direccion", "")
        usuario.rol        = request.POST.get("rol", usuario.rol)

        nueva_pass = request.POST.get("password1", "")
        if nueva_pass:
            usuario.set_password(nueva_pass)

        usuario.save()
        messages.success(request, "Usuario actualizado correctamente.")
        return redirect("dashboard_usuarios")

    return render(request, "dashboard/usuario_form.html", {"usuario": usuario})


@login_required
def dashboard_usuario_eliminar(request, usuario_id):
    if not es_admin(request.user):
        return redirect("home")

    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.user == usuario:
        messages.error(request, "No puedes eliminar tu propia cuenta.")
        return redirect("dashboard_usuarios")

    if request.method == "POST":
        usuario.delete()
        messages.success(request, "Usuario eliminado.")
        return redirect("dashboard_usuarios")

    return render(request, "dashboard/confirmar_eliminar.html", {
        "mensaje":      f"¿Eliminar al usuario '{usuario.username}'?",
        "cancelar_url": "/dashboard/usuarios/",
    })
