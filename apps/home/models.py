
from django.db import models
from apps.authentication.models import Empleados, Region, Comuna

class Prueba(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=50, verbose_name='Titulo')
    descripcion = models.CharField(max_length=100, verbose_name='Descripcion')


class TipoCondominio(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
    

class Condominio(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50)
    estado = models.CharField(max_length=10)
    tipo_condominio = models.ForeignKey(TipoCondominio, on_delete=models.CASCADE)
    region = models.IntegerField()
    comuna = models.IntegerField()
    region = models.ForeignKey(Region, on_delete=models.CASCADE) 
    comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE)
   

    def __str__(self):
        return self.nombre


class Propiedad(models.Model):
    SI_NO_CHOICES = [
        ('SI', 'Sí'),
        ('NO', 'No'),
    ]

    id = models.AutoField(primary_key=True) 
    numero_propiedad = models.IntegerField(unique=True)
    piso = models.IntegerField()
    estado = models.CharField(max_length=10)
    condominio = models.ForeignKey(Condominio, on_delete=models.CASCADE)
    estacionamiento = models.CharField(max_length=2, choices=SI_NO_CHOICES,default='NO')
    fecha_creacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Propiedad {self.id} {self.numero_propiedad} en piso {self.piso}"


class Residentes(models.Model):
    SI_NO_CHOICES = [
        ('SI', 'Sí'),
        ('NO', 'No'),
    ]
    id = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=12)
    nombres = models.CharField(max_length=50)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50)
    telefono = models.IntegerField()
    correo_electronico = models.CharField(max_length=50)
    propietario = models.CharField(max_length=2, choices=SI_NO_CHOICES)
    estado = models.CharField(max_length=10)
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"

class UbicacionEstacionamiento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=1)

    def __str__(self):
        return self.nombre
    
class TipoEstacionamiento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=1)

    def __str__(self):
        return self.nombre
    
class EstadoEstacionamiento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=1)

    def __str__(self):
        return self.nombre

class NumeroEstacionamiento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    estado = models.CharField(max_length=1)

    def __str__(self):
        return self.nombre
    
class Estacionamiento(models.Model):
    id = models.AutoField(primary_key=True)
    numero_estacionamiento = models.ForeignKey(NumeroEstacionamiento, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey(UbicacionEstacionamiento, on_delete=models.CASCADE)
    tipo_estacionamiento = models.ForeignKey(TipoEstacionamiento, on_delete=models.CASCADE)
    estado_estacionamiento = models.ForeignKey(EstadoEstacionamiento, on_delete=models.CASCADE)
    fecha_creacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Estacionamiento {self.numero_estacionamiento}"
    
class ReservaEstacionamiento(models.Model):
    id = models.AutoField(primary_key=True)
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE)
    estacionamiento = models.IntegerField(null=True, blank=True)  # Cambiar a IntegerField  
    empleado = models.ForeignKey(Empleados, on_delete=models.CASCADE)
    rut_visita = models.CharField(max_length=12)
    nombre_visita = models.CharField(max_length=50)
    apellido_paterno_visita = models.CharField(max_length=50)
    apellido_materno_visita = models.CharField(max_length=50)
    telefono_visita = models.CharField(max_length=10)
    relacion_residente = models.CharField(max_length=50)
    patente_vehiculo = models.CharField(max_length=8, null=True, blank=True)
    descripcion_vehiculo = models.CharField(max_length=100, null=True, blank=True)
    tiempo_permanencia = models.TimeField(null=True, blank=True)
    fecha_registro_visita = models.DateTimeField(auto_now_add=True)
    fecha_llegada_visita = models.DateTimeField(null=True, blank=True)
    fecha_llegada_visita_confirmada = models.DateTimeField(null=True, blank=True)
    fecha_fin_visita = models.DateTimeField(null=True, blank=True)
    fecha_modifica_reserva = models.DateTimeField(null=True, blank=True)
    estado_estacionamiento = models.CharField(max_length=25, null=True, blank=True)
    id_residente2 = models.IntegerField(null=True, blank=True) # trae el id del residente

    def __str__(self):
        return f"Reserva de {self.nombre_visita} {self.apellido_paterno_visita} para el estacionamiento {self.estacionamiento}"

class Observaciones(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=500)
    fecha_registro_observacion = models.DateTimeField(auto_now_add=True)
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleados, on_delete=models.CASCADE)

    def __str__(self):
        return f"Observación de {self.propiedad}"