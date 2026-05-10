from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Barbero, Servicio, Reserva


class UsuarioAdmin(UserAdmin):
    model = Usuario

    list_display = ("username", "email", "rol", "is_active")
    list_filter = ("rol", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)

    # EDITAR USUARIO (lo que se ve cuando entras a un usuario)
    fieldsets = (
        ("Datos del usuario", {"fields": ("username", "password")}),
        ("Información personal", {"fields": ("first_name", "last_name", "email", "telefono", "direccion")}),
        ("Rol y estado", {"fields": ("rol", "is_active")}),
    )

    # esto es lo que se ve cuando le das a Add user)
    add_fieldsets = (
        ("Crear usuario", {
            "classes": ("wide",),
            "fields": ("username", "email", "first_name", "last_name", "telefono", "direccion", "rol", "password1", "password2", "is_active"),
        }),
    )

    # Ocultar cosas innecesarias
    filter_horizontal = ()
    readonly_fields = ()


admin.site.register(Usuario, UsuarioAdmin)



@admin.register(Barbero)
class BarberoAdmin(admin.ModelAdmin):
    list_display = ("user", "especialidad", "disponible")


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "duracion_minutos", "activo")


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("cliente", "barbero", "servicio", "fecha", "hora", "estado")
    list_filter = ("estado", "fecha", "barbero")
