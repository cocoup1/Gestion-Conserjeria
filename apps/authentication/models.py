
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, User
from .validators import validate_rut
from django.db.models.signals import post_delete
from django.dispatch import receiver


class Rol(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)


   
class User(AbstractUser):
    SUPER_ADMIN = 'super_admin'
    ADMIN_CONDOMINIO = 'admin_condominio'
    CONSERJE = 'conserje'

    ROLE_CHOICES = [
        (SUPER_ADMIN, 'Super Administrador'),
        (ADMIN_CONDOMINIO, 'Administrador del Condominio'),
        (CONSERJE, 'Conserje'),
    ]

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, null=False, blank=True)  # Permitir null para evitar predeterminado 
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)

    objects = UserManager()
    
    def is_super_admin(self):
        return self.rol and self.rol.nombre == 'super_admin'

    def is_admin_condominio(self):
        return self.rol and self.rol.nombre == 'admin_condominio'

    def is_conserje(self):
        return self.rol and self.rol.nombre == 'conserje'   
    

    
class Region(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Comuna(models.Model):
    id_region = models.ForeignKey(Region, on_delete=models.CASCADE)
    #region = models.ForeignKey(Region, on_delete=models.CASCADE) luego volver gloria
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Empleados(models.Model):
    id = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=12, unique=True)  
    nombres = models.CharField(max_length=50)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50)
    direccion = models.CharField(max_length=70)
    telefono = models.IntegerField()
    correo_electronico = models.CharField(max_length=50)
    sexo = models.CharField(max_length=50)
    fecha_ingreso = models.DateField(null=True, blank=True)
    fecha_retiro = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=10)
    id_region = models.ForeignKey(Region, on_delete=models.CASCADE) 
    id_comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE)
    id_rol = models.ForeignKey(Rol, on_delete=models.CASCADE)  # Relación de muchos a muchos con Rol
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)  # Relación de uno a uno con User

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"

    def save(self, *args, **kwargs):
        if not self.id_rol:
            self.id_rol_id = 1  # Establecer el valor predeterminado para id_rol
        super().save(*args, **kwargs)


@receiver(post_delete, sender=Empleados)
def eliminar_usuario(sender, instance, **kwargs):
    if instance.usuario:
        instance.usuario.delete()