import pytest
from django.urls import reverse
from apps.authentication.models import Empleados, User, Rol, Region, Comuna
from django.contrib.auth.hashers import check_password




# @pytest.fixture
# def crear_usuario():
#     user = User.objects.create_user(username='maria.luz', email='maria.luz@example.com', password='prueba123')
#     return user

# @pytest.mark.django_db
# def test_listar_usuarios(client, crear_usuario):
#     user = User.objects.get(username='maria.luz')
#     assert user is not None


# @pytest.mark.django_db
# def test_listar_empleados(client):
#     # Obtener el usuario de la base de datos
#     user = User.objects.get(username='maria.luz')

#     # Verificar si la contraseña en texto claro es correcta
#     assert check_password('prueba123', user.password)  # Verifica el hash con la contraseña en texto claro

#     # Ahora intenta hacer login con la contraseña en texto claro
#     login_success = client.login(username='maria.luz', password='prueba123')
#     assert login_success is True, "El login falló"

#     # Hacer la solicitud GET
#     url = reverse('ver_conserjes')
#     response = client.get(url)

#     # Verificar que la respuesta sea correcta
#     assert response.status_code == 200





from datetime import date


# @pytest.mark.django_db
# def test_crear_empleado():
#     # Crear los objetos relacionados para el modelo Empleado
#     region = Region.objects.create(nombre='Santiago')
#     comuna = Comuna.objects.create(nombre='Providencia', id_region=region)  # Relación con Region
#     rol = Rol.objects.create(nombre='conserje')  # Asegúrate de que Rol tenga el nombre adecuado
#     usuario = User.objects.create_user(username='juan.perez', password='password123', email='juan.perez@example.com')

#     # Crear el empleado utilizando los objetos previamente creados
#     empleado = Empleados.objects.create(
#         rut='12345678-9',
#         nombres='Juan',
#         apellido_paterno='Pérez',
#         apellido_materno='González',
#         direccion='Calle Falsa 123',

#         telefono=123456789,
#         correo_electronico='juan@example.com',
#         sexo='Masculino',
#         fecha_ingreso='2024-01-01',
#         estado='Activo',
#         id_region=region,   # Asegúrate de pasar la relación correctamente
#         id_comuna=comuna,   # Asegúrate de pasar la relación correctamente
#         id_rol=rol,         # Asegúrate de pasar la relación correctamente
#         usuario=usuario     # Relación con el usuario
#     )

#     # Verificar que el empleado se guardó correctamente en la base de datos
#     assert empleado.id is not None
#     assert empleado.nombres == 'Juan'
#     assert empleado.apellido_paterno == 'Pérez'
#     assert empleado.apellido_materno == 'González'
#     assert empleado.direccion == 'Calle Falsa 123'
#     assert empleado.telefono == 123456789
#     assert empleado.correo_electronico == 'juan@example.com'
#     assert empleado.sexo == 'Masculino'
#     assert empleado.estado == 'Activo'
#     assert empleado.id_region == region  # Verificar la relación
#     assert empleado.id_comuna == comuna  # Verificar la relación
#     assert empleado.id_rol == rol        # Verificar la relación
#     assert empleado.usuario == usuario  # Verificar la relación con User



