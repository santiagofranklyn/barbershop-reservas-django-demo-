# from django import forms
# from django.contrib.auth.forms import (
#     UserCreationForm,
#     AuthenticationForm
# )

# from .models import Usuario, Reserva


# class RegistroForm(UserCreationForm):

#     class Meta:

#         model = Usuario

#         fields = [
#             'username',
#             'first_name',
#             'last_name',
#             'email',
#             'telefono',
#             'direccion',
#             'password1',
#             'password2'
#         ]


# class LoginForm(AuthenticationForm):
#     pass


# class ReservaForm(forms.ModelForm):

#     class Meta:
#         model = Reserva

#         fields = [
#             'barbero',
#             'servicio',
#             'fecha',
#             'hora'
#         ]