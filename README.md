
REQUISITOS
-----------
1. Este proyecto se ejecuta con python 3.9
2. mysql 8.0
3. instalar mysql connector 8.0
  https://downloads.mysql.com/archives/c-odbc/

  
CONFIGURACIÓN DE VARIABLES SEGUN AMBIENTE
-----------------------------------------
1. Ambiente local.- comentar variables globales de producción en el archivo .env
2. Ambiente Producción.- comentar variables globales para levantar local en el archivo .env


PASOS
-----
1. instalar python 3.9 o la version que usaras 3.12 por ejemplo en el equipo

ANTES DE CREAR EL PROEYCTO TIPO API DEBES CREAR EL ENTORNO VIRTUAL
--------------------------------------------------------------------------
2. Crear  el directorio que contendrá el proeycto, abrirlo con visual estudio code y dedse aqui crear y activar un nuevo entorno virtual con python 3.9 o el que usará.
  - > py -3.9 -m venv entorno
  - > .\entorno\Scripts\activate

2.1 Creo el proeycto con un punto (esto para qeu no cree el proeycto dentro de una carpeta nueva)
	(entorno1) PS C:\Project-mios\proyectoApi> django-admin startproject proyecto_api . 

3. Configuración de dependencias
   - El archivo requirements.txt se encuentra en la raíz del proyecto
   - Este archivo contiene la lista completa de dependencias de Python
   - El archivo está configurado y listo para la instalación.
SI NO TIENE EL ARCHIVO.- copiar el archivo .txt 

4. Configuracion del archivo settings.py
   - Configurar la conexión a la base de datos local o produción.

4. Instalción de dependencias
  - (entorno)... > pip install -r requirements.txt

5. Levantar el proyecto local
  - > python manage.py runserver 8081
. Indica que falta migraciones, omitir mensaje por ahora.
. Levantar el servidor de base de datos

5.1 CREAR LA APLICACION PRINCIPAL
	(entorno1) PS C:\Project-mios\proyectoApi> python manage.py startapp project


6. Crear la base de datos

7. Hacer las migraciones
  (entorno)...> python manage.py makemigrations
  (entorno)...> python manage.py migrate
. Para migraciones posteriores, eliminar la carpeta de migracion inicial y volver a migrar

8. Crear el super usuario desde la terminal
  (entorno)...> python manage.py createsuperuser
. Ingresar user=admin, correo, y pass

8. Llenar las tablas maestras
   - region, comuna, rol, estadoestacionamiento, numeroestacionamiento, tipoestacionamiento,               ubicacionestacionamiento, tipocondominio, estacionamiento, home_condominio, home_propiedad

      INSERT INTO conserjeria_10.home_estadoestacionamiento VALUES (1,'Disponible','1'),(2,'Ocupado','1'),(3,'Reservado','1'),(4,'En mantenimiento','1');

      INSERT INTO conserjeria_10.home_numeroestacionamiento VALUES (1,'A100','1'),(2,'A101','1'),(3,'A102','1'),(4,'B100','1'),(5,'B101','1'),(6,'B102','1'),(7,'B103','1'),(8,'B104','0');

      INSERT INTO conserjeria_10.home_tipoestacionamiento VALUES (1,'Visita','1'),(2,'Residente','1'),(3,'Discapacitados','1');
  
      INSERT INTO conserjeria_10.home_ubicacionestacionamiento VALUES (1,'NIvel -2','1'),(2,'Nivel -1','1'),(3,'Primer piso','1');

      INSERT INTO conserjeria_10.home_estacionamiento VALUES (1,'2024-11-16',1,1,1,3),(2,'2024-11-16',1,2,1,3),(3,'2024-11-16',1,4,1,2),(4,'2024-11-16',3,8,2,1),(6,'2024-11-23',1,3,1,3),(7,'2024-11-23',1,5,1,2),(8,'2024-11-23',1,6,1,2),(9,'2024-11-23',1,7,1,1);

      INSERT INTO conserjeria_10.home_condominio VALUES (1,'Los Alamos','Camino la Laguna','1',86,7,1);

      INSERT INTO conserjeria_10.home_propiedad VALUES (1,100,1,'1','NO','2024-10-26',1),(2,101,1,'1','SI','2024-10-26',1),(3,102,1,'1','SI','2024-11-24',1);

      INSERT INTO conserjeria_10.home_residentes VALUES (1,'14.750.183-8','Sonia','Apaza','Gutierrez',963382287,'residenteA@gmail.com','NO','activo',1),(2,'14.750.183-9','Francisco','Apaza','Gutierrez',963382287,'residenteB@gmail.com','NO','activo',1),(3,'14.750.183-1','Jorge','Apaza','Gutierrez',963382287,'residenteC@gmail.com','SI','activo',2),(4,'21.434.544-7','Luis','Flores','Torres',925325889,'asdas@sadsa.com','SI','1',1),(5,'14.750.183-2','Julio','Lopez','Oragon',987654321,'xxxxxx2@gmail.com','SI','activo',3);

8. Crear empleado Administrador del Condominio 
      0) Ingresar al panel de django como admin
      1) Crear User: ingresar los datos. Seleccionar rol admin-condominio.
      2) Crear Empleado: ingresar sus datos. 
      3) Ir a la base de datos y actualizar su clave (tabla user)

 . Todo administrador del condominio debe ser ingresado por el admin desde el portal de django.

9. Crear empleado Conserje (Desde la aplicación web)

SUBIR CAMBIOS DE MI RAMA


5. Ir al repositorio y hacer un pr. 



