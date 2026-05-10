#estas son las tablas que utlizara la base de datos de mi proyecto 
from django.db import models  #models trae las herramientas para crear tablas en Django.
from django.contrib.auth.models import AbstractUser  # AbstractUser es el modelo base de usuario de Django, pero para poder personalizarlo.


class Usuario(AbstractUser):  #con esto estoy creando un usuario personalizado que hereda lo que ya trae django
    telefono = models.CharField(max_length=20, blank=True, null=True)  
    direccion = models.TextField(blank=True, null=True)

    rol = models.CharField(
        max_length=20,
        choices=[  #con choice estoy obligando a que solo pueda utilizar esos tres valores 
            ('CLIENTE', 'Cliente'),
            ('BARBERO', 'Barbero'),
            ('ADMIN', 'Administrador')
        ],
        default='CLIENTE'   #con esto se crea la logica de que cada uno tenga permiso diferente 
    )

    def __str__(self):
        return self.username   # esto es como para que el usuario se muestre con el nombre digitado ante el admin


class Barbero(models.Model):
    user = models.OneToOneField(Usuario, on_delete=models.CASCADE) #esto es la relacion del usuario con el barbero que es de uno solo 
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_minutos = models.IntegerField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Reserva(models.Model):
    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("CONFIRMADA", "Confirmada"),
        ("RECHAZADA", "Rechazada"),
        ("CANCELADA", "Cancelada"),
    ]

    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="reservas_cliente")
    barbero = models.ForeignKey(Barbero, on_delete=models.CASCADE, related_name="reservas_barbero")
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)

    fecha = models.DateField()
    hora = models.TimeField()

    estado = models.CharField(max_length=20, choices=ESTADOS, default="PENDIENTE")

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('barbero', 'fecha', 'hora')  # evita doble reserva

    def __str__(self):
        return f"{self.cliente.username} - {self.servicio.nombre} - {self.fecha} {self.hora}"
