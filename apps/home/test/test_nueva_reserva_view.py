from django.test import TestCase, Client
from django.urls import reverse
from datetime import datetime, time
from apps.home.models import ReservaEstacionamiento, Propiedad, Empleados

class ReservaEstacionamientoTestCase(TestCase):
    def setUp(self):
        # Inicializar datos necesarios para las pruebas
        self.client = Client()
        self.crear_reserva_url = reverse('crear_reserva')  # Asegúrate de que la URL esté configurada correctamente
        
        # Crear una propiedad de prueba
        self.propiedad = Propiedad.objects.create(
            nombre="Propiedad 1",
            direccion="123 Calle Principal"
        )
        
        # Crear un empleado de prueba
        self.empleado = Empleados.objects.create(
            nombres="Juan",
            apellido_paterno="Pérez"
        )
    
    def test_crear_reserva_exito(self):
        # Datos para crear una reserva exitosa
        data = {
            'propiedad': self.propiedad.id,
            'estacionamiento': 5,
            'empleado': self.empleado.id,
            'rut_visita': '12345678-9',
            'nombre_visita': 'Carlos',
            'apellido_paterno_visita': 'Gómez',
            'apellido_materno_visita': 'Soto',
            'telefono_visita': '987654321',
            'relacion_residente': 'Amigo',
            'patente_vehiculo': 'AB123CD',
            'descripcion_vehiculo': 'Auto rojo',
            'tiempo_permanencia': time(2, 30),  # 2 horas y 30 minutos
            'fecha_llegada_visita': datetime(2024, 12, 4, 15, 30),
        }

        response = self.client.post(self.crear_reserva_url, data)
        self.assertEqual(response.status_code, 201)  # Suponiendo que se utiliza este código para éxito en creación
        
        # Verificar que la reserva se haya creado correctamente
        reserva = ReservaEstacionamiento.objects.get(rut_visita=data['rut_visita'])
        self.assertEqual(reserva.nombre_visita, data['nombre_visita'])
        self.assertEqual(reserva.estacionamiento, data['estacionamiento'])
        self.assertEqual(reserva.patente_vehiculo, data['patente_vehiculo'])
    
    def test_crear_reserva_error_datos_faltantes(self):
        # Datos incompletos para crear una reserva
        data = {
            'propiedad': self.propiedad.id,
            'empleado': self.empleado.id,
            'rut_visita': '12345678-9',
        }

        response = self.client.post(self.crear_reserva_url, data)
        self.assertEqual(response.status_code, 400)  # Código de error por datos incompletos
        
        # Verificar que no se haya creado la reserva
        reservas = ReservaEstacionamiento.objects.filter(rut_visita=data['rut_visita'])
        self.assertEqual(reservas.count(), 0)
