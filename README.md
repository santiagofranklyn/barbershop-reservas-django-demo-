# BarberShop - Sistema de Reservas

Proyecto desarrollado en Django.

# funcionalidaes
- Registro y Login
- Roles: Cliente / Barbero / Admin
- Reservas con estado: Pendiente, Confirmada, Rechazada, Cancelada
- Evita doble reserva (misma fecha/hora/barbero)
- Panel admin para gestión de usuarios, servicios y barberos

# Tecnologías
- Python
- Django
- SQLite
- HTML/CSS

# Instalación
1. Clonar repositorio
2. Crear entorno virtual
3. Instalar dependencias:
   pip install -r requirements.txt
4. Ejecutar migraciones:
   python manage.py migrate
5. Ejecutar servidor:
   python manage.py runserver