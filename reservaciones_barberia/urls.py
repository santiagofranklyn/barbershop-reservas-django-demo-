from django.urls import path
from . import views

urlpatterns = [
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
]


