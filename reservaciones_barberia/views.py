from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Barbero, Servicio, Reserva, Usuario


def home(request):
    servicios = Servicio.objects.filter(activo=True)
    barberos = Barbero.objects.filter(disponible=True)

    return render(request, "home.html", {"servicios": servicios, "barberos": barberos})


def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        telefono = request.POST.get("telefono")
        direccion = request.POST.get("direccion")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect("register")

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, "Ese usuario ya existe.")
            return redirect("register")

        user = Usuario.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            telefono=telefono,
            direccion=direccion,
            rol="CLIENTE"
        )

        login(request, user)
        messages.success(request, "Cuenta creada correctamente.")
        return redirect("home")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def servicios_view(request):
    servicios = Servicio.objects.filter(activo=True)
    return render(request, "servicios.html", {"servicios": servicios})


def barberos_view(request):
    barberos = Barbero.objects.filter(disponible=True)
    return render(request, "barberos.html", {"barberos": barberos})


@login_required
def reservar_view(request):
    if request.method == "POST":
        barbero_id = request.POST.get("barbero")
        servicio_id = request.POST.get("servicio")
        fecha = request.POST.get("fecha")
        hora = request.POST.get("hora")

        barbero = get_object_or_404(Barbero, id=barbero_id)
        servicio = get_object_or_404(Servicio, id=servicio_id)

        if Reserva.objects.filter(barbero=barbero, fecha=fecha, hora=hora).exists():
            messages.error(request, "Ese horario ya está reservado con este barbero.")
            return redirect("reservas")

        reserva = Reserva.objects.create(
            cliente=request.user,
            barbero=barbero,
            servicio=servicio,
            fecha=fecha,
            hora=hora,
            estado="PENDIENTE"
        )

        return redirect("confirmacion", reserva_id=reserva.id)

    servicios = Servicio.objects.filter(activo=True)
    barberos = Barbero.objects.filter(disponible=True)

    return render(request, "reservas.html", {"servicios": servicios, "barberos": barberos})


@login_required
def confirmacion_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)
    return render(request, "confirmacion.html", {"reserva": reserva})


@login_required
def mis_reservas_view(request):
    reservas = Reserva.objects.filter(cliente=request.user).order_by("-creado_en")
    return render(request, "Mis_Reservas.html", {"reservas": reservas})


@login_required
def cancelar_reserva_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)

    if reserva.estado != "PENDIENTE":
        messages.error(request, "Solo puedes cancelar una reserva pendiente.")
        return redirect("mis_reservas")

    reserva.estado = "CANCELADA"
    reserva.save()

    messages.success(request, "Reserva cancelada correctamente.")
    return redirect("mis_reservas")


def es_barbero(user):
    return user.rol == "BARBERO"


@login_required
def agenda_view(request):
    if not es_barbero(request.user):
        messages.error(request, "No tienes permisos para entrar aquí.")
        return redirect("home")

    barbero = get_object_or_404(Barbero, user=request.user)
    reservas = Reserva.objects.filter(barbero=barbero).order_by("-creado_en")

    return render(request, "agenda.html", {"reservas": reservas, "barbero": barbero})


@login_required
def cambiar_estado_reserva(request, reserva_id, estado):
    if not es_barbero(request.user):
        return redirect("home")

    barbero = get_object_or_404(Barbero, user=request.user)
    reserva = get_object_or_404(Reserva, id=reserva_id, barbero=barbero)

    if reserva.estado != "PENDIENTE":
        messages.error(request, "Solo puedes modificar reservas pendientes.")
        return redirect("agenda")

    if estado not in ["CONFIRMADA", "RECHAZADA"]:
        return redirect("agenda")

    reserva.estado = estado
    reserva.save()

    messages.success(request, "Estado actualizado correctamente.")
    return redirect("agenda")


@login_required
def clientes_view(request):
    if not (request.user.is_superuser or request.user.rol == "ADMIN"):
        messages.error(request, "No tienes permisos para ver esta sección.")
        return redirect("home")

    clientes = Usuario.objects.filter(rol="CLIENTE")
    return render(request, "clientes.html", {"clientes": clientes})