# import pytest
# from django.urls import reverse
# from apps.authentication.models import Empleados, User, Rol, Region, Comuna
# from django.contrib.auth.hashers import check_password

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Rol, Empleados

User = get_user_model()

class LoginViewTestCase(TestCase):
    def setUp(self):
        # Configurar los datos iniciales para las pruebas
        self.client = Client()
        self.login_url = reverse('login')  # Asegúrate de que el nombre de tu vista sea 'login'
        
        # Crear un rol de super_admin
        self.super_admin_role = Rol.objects.create(nombre='super_admin', descripcion='Super Administrador')
        
        # Crear un usuario super_admin
        self.super_admin_user = User.objects.create_user(
            username='superadmin',
            email='superadmin@test.com',
            password='password123',
            role=User.SUPER_ADMIN,
            rol=self.super_admin_role
        )
        
        # Crear un rol de administrador de condominio
        self.admin_role = Rol.objects.create(nombre='admin_condominio', descripcion='Administrador del Condominio')
        
        # Crear un usuario administrador de condominio
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='password123',
            role=User.ADMIN_CONDOMINIO,
            rol=self.admin_role
        )
        
        # Crear un empleado asociado al administrador
        self.empleado = Empleados.objects.create(
            usuario=self.admin_user,
            nombres="Juan",
            apellido_paterno="Pérez"
        )
    
    def test_login_super_admin(self):
        # Probar inicio de sesión como super_admin
        response = self.client.post(self.login_url, {
            'username': 'superadmin',
            'password': 'password123'
        })
        self.assertRedirects(response, "/")  # Redirige al dashboard
        self.assertIn('username', self.client.session)
        self.assertEqual(self.client.session['username'], 'superadmin')

    def test_login_admin_with_employee(self):
        # Probar inicio de sesión como admin_condominio con empleado asociado
        response = self.client.post(self.login_url, {
            'username': 'admin',
            'password': 'password123'
        })
        self.assertRedirects(response, "/")  # Redirige al dashboard
        self.assertIn('username', self.client.session)
        self.assertIn('empleado_id', self.client.session)
        self.assertIn('nombre_empleado', self.client.session)
        self.assertEqual(self.client.session['username'], 'admin')
        self.assertEqual(self.client.session['empleado_id'], self.empleado.id)
        self.assertEqual(self.client.session['nombre_empleado'], "Juan Pérez")

    def test_login_invalid_credentials(self):
        # Probar inicio de sesión con credenciales inválidas
        response = self.client.post(self.login_url, {
            'username': 'invaliduser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Credenciales inválidas')
