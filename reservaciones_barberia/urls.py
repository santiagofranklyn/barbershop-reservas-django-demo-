from django.urls import path
from . import views
from . import dashboard_views

urlpatterns = [
    # ── Sitio público ──────────────────────────────────────────
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    path("servicios/", views.servicios_view, name="servicios"),
    path("clientes/", views.clientes_view, name="clientes"),
    path("barberos/", views.barberos_view, name="barberos"),

    path("reservas/", views.reservar_view, name="reservas"),
    path("confirmacion/<int:reserva_id>/", views.confirmacion_view, name="confirmacion"),
    path("mis-reservas/", views.mis_reservas_view, name="mis_reservas"),
    path("cancelar/<int:reserva_id>/", views.cancelar_reserva_view, name="cancelar_reserva"),

    path("agenda/", views.agenda_view, name="agenda"),
    path("agenda/<int:reserva_id>/<str:estado>/", views.cambiar_estado_reserva, name="cambiar_estado_reserva"),

    # ── Dashboard admin ────────────────────────────────────────
    path("dashboard/", dashboard_views.dashboard_home, name="dashboard_home"),

    # Reservas
    path("dashboard/reservas/", dashboard_views.dashboard_reservas, name="dashboard_reservas"),
    path("dashboard/reservas/<int:reserva_id>/editar/", dashboard_views.dashboard_reserva_editar, name="dashboard_reserva_editar"),
    path("dashboard/reservas/<int:reserva_id>/eliminar/", dashboard_views.dashboard_reserva_eliminar, name="dashboard_reserva_eliminar"),

    # Barberos
    path("dashboard/barberos/", dashboard_views.dashboard_barberos, name="dashboard_barberos"),
    path("dashboard/barberos/crear/", dashboard_views.dashboard_barbero_crear, name="dashboard_barbero_crear"),
    path("dashboard/barberos/<int:barbero_id>/editar/", dashboard_views.dashboard_barbero_editar, name="dashboard_barbero_editar"),
    path("dashboard/barberos/<int:barbero_id>/eliminar/", dashboard_views.dashboard_barbero_eliminar, name="dashboard_barbero_eliminar"),

    # Servicios
    path("dashboard/servicios/", dashboard_views.dashboard_servicios, name="dashboard_servicios"),
    path("dashboard/servicios/crear/", dashboard_views.dashboard_servicio_crear, name="dashboard_servicio_crear"),
    path("dashboard/servicios/<int:servicio_id>/editar/", dashboard_views.dashboard_servicio_editar, name="dashboard_servicio_editar"),
    path("dashboard/servicios/<int:servicio_id>/toggle/", dashboard_views.dashboard_servicio_toggle, name="dashboard_servicio_toggle"),
    path("dashboard/servicios/<int:servicio_id>/eliminar/", dashboard_views.dashboard_servicio_eliminar, name="dashboard_servicio_eliminar"),

    # Usuarios
    path("dashboard/usuarios/", dashboard_views.dashboard_usuarios, name="dashboard_usuarios"),
    path("dashboard/usuarios/crear/", dashboard_views.dashboard_usuario_crear, name="dashboard_usuario_crear"),
    path("dashboard/usuarios/<int:usuario_id>/editar/", dashboard_views.dashboard_usuario_editar, name="dashboard_usuario_editar"),
    path("dashboard/usuarios/<int:usuario_id>/eliminar/", dashboard_views.dashboard_usuario_eliminar, name="dashboard_usuario_eliminar"),
]




