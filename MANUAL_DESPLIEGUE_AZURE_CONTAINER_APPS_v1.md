# Manual de Despliegue - Django en Azure Container Apps

**Proyecto:** Sistema de Gestión de Conserjería  
**Fecha:** 30 de Diciembre de 2025  
**Objetivo:** Desplegar aplicación Django usando contenedores en Azure Container Apps con MySQL Flexible Server

---

## Tabla de Contenidos
1. [Requisitos Previos](#requisitos-previos)
2. [Autenticación en Azure](#autenticación-en-azure)
3. [Creación de Infraestructura](#creación-de-infraestructura)
4. [Configuración de la Aplicación](#configuración-de-la-aplicación)
5. [Construcción y Despliegue](#construcción-y-despliegue)
6. [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
7. [Migraciones y Base de Datos](#migraciones-y-base-de-datos)
8. [Verificación y Pruebas](#verificación-y-pruebas)
9. [Comandos de Mantenimiento](#comandos-de-mantenimiento)

---

## Requisitos Previos

### Software Necesario
- Azure CLI instalado
- Docker (opcional, ACR puede construir las imágenes)
- Python 3.12
- MySQL Workbench (para gestión de BD)

### Conocimientos
- Conceptos básicos de Docker
- Django Framework
- Azure CLI
- MySQL

---

## Autenticación en Azure

### Paso 1: Iniciar sesión en Azure

```powershell
# Autenticación con tenant específico
az login --tenant 4640988d-3358-44cc-badf-7e3c93497ab3
```

**Nota:** Usar el tenant correcto es crucial. Verificar en Azure Portal > Azure Active Directory.

### Paso 2: Verificar suscripción activa

```powershell
# Listar suscripciones disponibles
az account list --output table

# Establecer suscripción activa
az account set --subscription dea554ce-8eea-41eb-8579-d6a436a70073

# Verificar suscripción actual
az account show
```

---

## Creación de Infraestructura

### Paso 3: Crear Grupo de Recursos

```powershell
az group create `
  --name gr-coserjeria02 `
  --location brazilsouth
```

**Regiones disponibles:** Chile Central no soporta Container Apps ni ACR Build. Usar Brazil South.

### Paso 4: Crear MySQL Flexible Server

```powershell
# Crear servidor MySQL
az mysql flexible-server create `
  --resource-group gr-coserjeria02 `
  --name servidor-conserjeria02 `
  --location chilecentralz `
  --admin-user Javier `
  --admin-password "Estrella.23" `
  --sku-name Standard_B1ms `
  --tier Burstable `
  --public-access 0.0.0.0-255.255.255.255 `
  --version 8.0.21 `
  --storage-size 20
```

**Importante:**
- `--public-access 0.0.0.0-255.255.255.255`: Permite conexiones desde cualquier IP (ajustar en producción)
- `Standard_B1ms`: SKU económico para desarrollo
- El servidor viene con `require_secure_transport=ON` por defecto

### Paso 5: Crear Base de Datos

```powershell
# Listar bases de datos existentes
az mysql flexible-server db list `
  --resource-group gr-coserjeria02 `
  --server-name servidor-conserjeria02

# La base de datos por defecto es: flexibleserverdb
```

**Nota:** MySQL Flexible Server crea automáticamente `flexibleserverdb`. Usar este nombre en la configuración.

### Paso 6: Crear Azure Container Registry

```powershell
az acr create `
  --resource-group gr-coserjeria02 `
  --name acrconserjeria02br `
  --sku Basic `
  --location brazilsouth
```

**Nota:** Los nombres de ACR no pueden contener guiones, solo caracteres alfanuméricos.

### Paso 7: Habilitar Admin en ACR

```powershell
az acr update `
  --name acrconserjeria02br `
  --admin-enabled true

# Obtener credenciales
az acr credential show --name acrconserjeria02br
```

**Guardar:** `username` y `password` para configurar Container App.

### Paso 8: Crear Container Apps Environment

```powershell
az containerapp env create `
  --name env-conserjeria02 `
  --resource-group gr-coserjeria02 `
  --location brazilsouth
```

---

## Configuración de la Aplicación

### Paso 9: Descargar Certificado SSL para MySQL

```powershell
# Descargar certificado DigiCert Global Root G2
Invoke-WebRequest `
  -Uri "https://cacerts.digicert.com/DigiCertGlobalRootG2.crt.pem" `
  -OutFile "DigiCertGlobalRootG2.crt.pem"
```

**Ubicación:** Colocar en la raíz del proyecto Django.

### Paso 10: Configurar settings.py

**Archivo:** `core/settings.py`

```python
# Configuración de ALLOWED_HOSTS
ALLOWED_HOSTS = env.list(
    'ALLOWED_HOSTS',
    default=['.azurecontainerapps.io', 'localhost', '127.0.0.1']
)

# Configuración de CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    'https://app-conserjeria02.ashyhill-67264477.brazilsouth.azurecontainerapps.io',
    'http://127.0.0.1:8081'
]

# Configuración de Base de Datos con SSL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME', default='flexibleserverdb'),
        'USER': env('DB_USER', default='Javier'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='servidor-conserjeria02.mysql.database.azure.com'),
        'PORT': env('DB_PORT', default='3306'),
        'OPTIONS': {
            'ssl': {
                'ca': os.path.join(BASE_DIR, 'DigiCertGlobalRootG2.crt.pem')
            }
        }
    }
}
```

### Paso 11: Verificar Dockerfile

**Archivo:** `Dockerfile`

```dockerfile
FROM python:3.12-slim-bullseye

# Instalar dependencias del sistema para xhtml2pdf
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango1.0-dev \
    libcairo2-dev \
    libgdk-pixbuf2.0-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN python manage.py collectstatic --noinput || echo "Collectstatic failed, will run at startup"

EXPOSE 8000

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "600", "--workers", "2"]
```

---

## Construcción y Despliegue

### Paso 12: Construir Imagen en ACR

```powershell
# Construcción remota en Azure Container Registry
az acr build `
  --registry acrconserjeria02br `
  --image conserjeria:latest `
  .
```

**Ventajas de ACR Build:**
- No requiere Docker local
- Construcción en la nube optimizada
- Automáticamente sube la imagen al registro

**Tiempo aproximado:** 2-3 minutos

### Paso 13: Crear Container App

```powershell
az containerapp create `
  --name app-conserjeria02 `
  --resource-group gr-coserjeria02 `
  --environment env-conserjeria02 `
  --image acrconserjeria02br.azurecr.io/conserjeria:latest `
  --target-port 8000 `
  --ingress external `
  --registry-server acrconserjeria02br.azurecr.io `
  --registry-username acrconserjeria02br `
  --registry-password <PASSWORD_DEL_ACR> `
  --cpu 0.5 `
  --memory 1Gi `
  --min-replicas 0 `
  --max-replicas 10
```

**Parámetros importantes:**
- `--min-replicas 0`: Escala a cero para minimizar costos
- `--max-replicas 10`: Escalado automático según demanda
- `--ingress external`: Aplicación accesible desde internet
- `--cpu 0.5 --memory 1Gi`: Recursos suficientes para Django

---

## Configuración de Variables de Entorno

### Paso 14: Configurar Variables de Entorno

```powershell
# Configurar todas las variables necesarias
az containerapp update `
  --name app-conserjeria02 `
  --resource-group gr-coserjeria02 `
  --set-env-vars `
    SECRET_KEY="<TU_SECRET_KEY_DE_DJANGO>" `
    DB_NAME=flexibleserverdb `
    DB_USER=Javier `
    DB_PASSWORD="Estrella.23" `
    DB_HOST=servidor-conserjeria02.mysql.database.azure.com `
    DB_PORT=3306 `
    DEBUG=False `
    ALLOWED_HOSTS=".azurecontainerapps.io,localhost,127.0.0.1" `
    ASSETS_ROOT="/static/assets"
```

**Generar SECRET_KEY en Django:**
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Paso 15: Verificar Variables

```powershell
# Ver configuración actual
az containerapp show `
  --name app-conserjeria02 `
  --resource-group gr-coserjeria02 `
  --query properties.template.containers[0].env
```

---

## Migraciones y Base de Datos

### Paso 16: Migrar Base de Datos Local a Azure

**Opción 1: Usando MySQL Workbench**
1. Conectar a servidor local
2. Exportar base de datos (Data Export)
3. Conectar a Azure MySQL: `servidor-conserjeria02.mysql.database.azure.com`
4. Importar base de datos (Data Import)

**Opción 2: Usando mysqldump**
```bash
# Exportar
mysqldump -u root -p dbconserjeria02 > backup.sql

# Importar a Azure
mysql -h servidor-conserjeria02.mysql.database.azure.com \
  -u Javier -p flexibleserverdb < backup.sql
```

### Paso 17: Registrar Migraciones en Django

```powershell
# Conectar al contenedor y ejecutar migraciones
az containerapp exec `
  --name app-conserjeria02 `
  --resource-group gr-coserjeria02 `
  --command "python manage.py migrate --fake-initial"
```

**`--fake-initial`:** Registra las migraciones sin intentar crear tablas que ya existen.

---

## Verificación y Pruebas

### Paso 18: Obtener URL de la Aplicación

```powershell
az containerapp show `
  --name app-conserjeria02 `
  --resource-group gr-coserjeria02 `
  --query properties.configuration.ingress.fqdn `
  --output tsv
```

**URL obtenida:** `https://app-conserjeria02.ashyhill-67264477.brazilsouth.azurecontainerapps.io`

### Paso 19: Verificar Logs

```powershell
# Ver logs en tiempo real
az containerapp logs show `
  --name app-conserjeria02 `
  --resource-group gr-coserjeria02 `
  --follow

# Ver logs recientes
az containerapp logs show `
  --name app-conserjeria02 `
  --resource-group gr-coserjeria02 `
  --tail 100
```

### Paso 20: Probar Conexión a Base de Datos

```powershell
# Ejecutar comando en el contenedor
az containerapp exec `
  --name app-conserjeria02 `
  --resource-group gr-coserjeria02 `
  --command "python manage.py check --database default"
```

---

## Comandos de Mantenimiento

### Actualizar Aplicación

```powershell
# 1. Reconstruir imagen con cambios
az acr build `
  --registry acrconserjeria02br `
  --image conserjeria:latest `
  .

# 2. Actualizar Container App con nueva imagen
az containerapp update `
  --name app-conserjeria02 `
  --resource-group gr-coserjeria02 `
  --image acrconserjeria02br.azurecr.io/conserjeria:latest
```

### Escalar Aplicación

```powershell
# Escalar manualmente
az containerapp update `
  --name app-conserjeria02 `
  --resource-group gr-coserjeria02 `
  --min-replicas 1 `
  --max-replicas 5
```

### Ver Estado de Recursos

```powershell
# Estado del Container App
az containerapp show `
  --name app-conserjeria02 `
  --resource-group gr-coserjeria02

# Estado del MySQL Server
az mysql flexible-server show `
  --resource-group gr-coserjeria02 `
  --name servidor-conserjeria02

# Estado del ACR
az acr show `
  --name acrconserjeria02br `
  --resource-group gr-coserjeria02
```

### Reiniciar Aplicación

```powershell
# Forzar nueva revisión (reinicio)
az containerapp revision restart `
  --name app-conserjeria02 `
  --resource-group gr-coserjeria02
```

### Ejecutar Comandos Django

```powershell
# Shell interactivo
az containerapp exec `
  --name app-conserjeria02 `
  --resource-group gr-coserjeria02 `
  --command "/bin/bash"

# Crear superusuario
az containerapp exec `
  --name app-conserjeria02 `
  --resource-group gr-coserjeria02 `
  --command "python manage.py createsuperuser"

# Collect static files
az containerapp exec `
  --name app-conserjeria02 `
  --resource-group gr-coserjeria02 `
  --command "python manage.py collectstatic --noinput"
```

---

## Problemas Comunes y Soluciones

### Error: CSRF verification failed

**Problema:** Token CSRF inválido al enviar formularios.

**Solución:** Actualizar `CSRF_TRUSTED_ORIGINS` en `settings.py`:
```python
CSRF_TRUSTED_ORIGINS = [
    'https://app-conserjeria02.ashyhill-67264477.brazilsouth.azurecontainerapps.io',
]
```

### Error: Unknown database

**Problema:** Django no encuentra la base de datos.

**Solución:** Verificar nombre correcto de la base de datos:
```powershell
az mysql flexible-server db list `
  --resource-group gr-coserjeria02 `
  --server-name servidor-conserjeria02
```

Usar `flexibleserverdb` como `DB_NAME`.

### Error: SSL certificate verification failed

**Problema:** Certificado SSL no válido para MySQL.

**Solución:** 
1. Descargar certificado correcto: `DigiCertGlobalRootG2.crt.pem`
2. Colocar en raíz del proyecto
3. Configurar en `settings.py`:
```python
'OPTIONS': {
    'ssl': {
        'ca': os.path.join(BASE_DIR, 'DigiCertGlobalRootG2.crt.pem')
    }
}
```
4. Reconstruir imagen

### Error: Image pull failed

**Problema:** Container App no puede descargar imagen del ACR.

**Solución:** Verificar credenciales del ACR:
```powershell
az acr credential show --name acrconserjeria02br
```
Actualizar credenciales en Container App.

---

## Arquitectura Final

```
┌─────────────────────────────────────────────────────────┐
│                     INTERNET                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────────┐
│        Azure Container Apps (Brazil South)              │
│  ┌───────────────────────────────────────────────────┐  │
│  │  app-conserjeria02                                │  │
│  │  - Django 5.2.7 + Gunicorn                        │  │
│  │  - Python 3.12                                    │  │
│  │  - CPU: 0.5 vCPU, RAM: 1GB                        │  │
│  │  - Auto-scaling: 0-10 replicas                    │  │
│  └───────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ SSL/TLS (Port 3306)
                     ▼
┌─────────────────────────────────────────────────────────┐
│     Azure MySQL Flexible Server (Chile Central)         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  servidor-conserjeria02.mysql.database.azure.com │  │
│  │  - MySQL 8.0.21                                   │  │
│  │  - SKU: Standard_B1ms                             │  │
│  │  - Storage: 20 GB                                 │  │
│  │  - Database: flexibleserverdb                     │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│   Azure Container Registry (Brazil South)               │
│  ┌───────────────────────────────────────────────────┐  │
│  │  acrconserjeria02br.azurecr.io                    │  │
│  │  - Image: conserjeria:latest                      │  │
│  │  - SKU: Basic                                     │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Costos Estimados (USD/mes)

| Servicio | Configuración | Costo Aprox. |
|----------|--------------|--------------|
| Container Apps | 0.5 vCPU, 1GB RAM, scale to zero | $5-15 |
| MySQL Flexible Server | Standard_B1ms, 20GB | $15-25 |
| Container Registry | Basic | $5 |
| **TOTAL ESTIMADO** | | **$25-45/mes** |

**Nota:** Costos varían según uso real. Scale-to-zero minimiza costos de Container Apps.

---

## Checklist de Despliegue

- [ ] Azure CLI instalado y configurado
- [ ] Autenticación en tenant correcto
- [ ] Grupo de recursos creado
- [ ] MySQL Flexible Server creado
- [ ] Base de datos creada/migrada
- [ ] Container Registry creado y configurado
- [ ] Container Apps Environment creado
- [ ] Certificado SSL descargado
- [ ] settings.py configurado correctamente
- [ ] Dockerfile verificado
- [ ] Imagen construida en ACR
- [ ] Container App creado
- [ ] Variables de entorno configuradas
- [ ] Migraciones ejecutadas
- [ ] CSRF_TRUSTED_ORIGINS actualizado
- [ ] Aplicación accesible y funcional
- [ ] Login y funcionalidades probadas

---

## Referencias

- [Azure Container Apps Documentation](https://learn.microsoft.com/azure/container-apps/)
- [Azure MySQL Flexible Server](https://learn.microsoft.com/azure/mysql/flexible-server/)
- [Azure Container Registry](https://learn.microsoft.com/azure/container-registry/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)

---

## Información del Proyecto

**Recursos Creados:**
- Grupo de Recursos: `gr-coserjeria02`
- MySQL Server: `servidor-conserjeria02.mysql.database.azure.com`
- Database: `flexibleserverdb`
- Container Registry: `acrconserjeria02br.azurecr.io`
- Container App: `app-conserjeria02`
- Environment: `env-conserjeria02`
- URL: `https://app-conserjeria02.ashyhill-67264477.brazilsouth.azurecontainerapps.io`

**Región Principal:** Brazil South (Container Apps + ACR)  
**Región Secundaria:** Chile Central (MySQL)

**Credenciales:**
- MySQL User: `Javier`
- MySQL Password: `Estrella.23`
- Database: `flexibleserverdb`

---

*Documento creado el 30 de Diciembre de 2025*
