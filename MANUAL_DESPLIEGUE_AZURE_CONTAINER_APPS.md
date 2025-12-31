# Manual de Despliegue Optimizado - Azure Container Apps

## 📋 Índice
1. [Introducción](#introducción)
2. [Estrategia de Costos](#estrategia-de-costos)
3. [Requisitos Previos](#requisitos-previos)
4. [Arquitectura](#arquitectura)
5. [Despliegue Paso a Paso](#despliegue-paso-a-paso)
6. [Configuración de Alertas de Presupuesto](#configuración-de-alertas-de-presupuesto)
7. [Eliminación de Recursos](#eliminación-de-recursos)
8. [Troubleshooting](#troubleshooting)
9. [Estimación de Costos](#estimación-de-costos)

---

## 🎯 Introducción

Este manual describe el despliegue optimizado de la aplicación **Gestión de Conserjería** en Azure Container Apps, diseñado específicamente para **portafolios y demostraciones**, priorizando el control de costos.

### Características principales:
- ✅ **Costo $0** cuando no está en uso
- ✅ Escalado automático a 0 réplicas
- ✅ Despliegue rápido (~45-60 minutos)
- ✅ Fácil eliminación de recursos
- ✅ Base de datos con backup para restauración rápida

---

## 💰 Estrategia de Costos

### Objetivo: Mantener costos < $3 USD/mes

#### Recursos a desplegar:
| Recurso | Costo Mensual | Costo Diario | Estrategia |
|---------|---------------|--------------|------------|
| **Container Apps** | ~$0.50-2 | ~$0.02-0.07 | Min replicas: 0 (escala a 0 cuando no hay tráfico) |
| **PostgreSQL Flexible** | ~$8-15 | ~$0.27-0.50 | **Solo crear cuando sea necesario**, eliminar después |
| **Container Registry** | $0 | $0 | Usar Docker Hub (gratuito) en lugar de ACR |
| **Container Environment** | Incluido | Incluido | Sin costo adicional con min replicas: 0 |

#### Costo real estimado:
- **Sin base de datos**: ~$0.50-1/mes (solo Container Apps inactivo)
- **Con base de datos activa 1 día**: ~$0.50 adicional
- **Con base de datos activa todo el mes**: ~$8-10/mes

### ⚠️ Recomendación para Portafolio:
**Elimina todos los recursos después de cada demo** y redespliega solo cuando un reclutador lo solicite. Esto mantiene el costo en $0 USD.

---

## 📦 Requisitos Previos

### 1. Software instalado:
- [x] Azure CLI instalado y actualizado
- [x] Docker Desktop instalado y corriendo
- [x] Git instalado
- [x] Cuenta de Docker Hub (gratuita)

### 2. Acceso a Azure:
- [x] Suscripción de Azure activa
- [x] Permisos para crear recursos

### 3. Archivos necesarios:
- [x] Código fuente de la aplicación
- [x] `backup_db.sql` con datos de la base de datos
- [x] `DigiCertGlobalRootG2.crt.pem` para conexión SSL a PostgreSQL

### 4. Verificaciones previas:
```bash
# Verificar Azure CLI
az --version

# Login en Azure
az login

# Verificar Docker
docker --version

# Verificar que Docker está corriendo
docker ps
```

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────┐
│         Internet / Usuarios                     │
└────────────────┬────────────────────────────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────┐
│    Azure Container Apps (Django App)            │
│    - Min replicas: 0 (escala a 0)              │
│    - Max replicas: 5                            │
│    - Puerto: 8000                               │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Azure Database for PostgreSQL Flexible Server  │
│    - Burstable tier B1ms                        │
│    - SSL habilitado                             │
│    - Puerto: 5432                               │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│         Docker Hub (Container Registry)         │
│    - Repositorio público (gratis)               │
│    - Imagen: tu-usuario/gestion-conserjeria     │
└─────────────────────────────────────────────────┘
```

### Decisiones de Arquitectura:

| Decisión | Razón |
|----------|-------|
| Docker Hub vs ACR | Ahorra $5/mes, suficiente para portafolio |
| Min replicas: 0 | Costo $0 cuando no hay tráfico |
| PostgreSQL Flexible | Tier más económico con auto-pause (si aplica) |
| Grupo de recursos único | Fácil eliminación completa |

---

## 🚀 Despliegue Paso a Paso

### Fase 1: Preparación (5 min)

#### 1.1 Login en Docker Hub
```bash
docker login
# Ingresa tu usuario y password de Docker Hub
```

#### 1.2 Configurar variables de entorno
```bash
# Variables generales
RESOURCE_GROUP="rg-gestion-conserjeria"
LOCATION="brazilsouth"
ACR_NAME="acrconserjer ia02br"  # Ya no se usará ACR, usar Docker Hub
DOCKER_HUB_USER="tu-usuario-dockerhub"
APP_NAME="app-conserjeria02"
ENV_NAME="env-conserjeria02"
DB_SERVER_NAME="psql-conserjeria02"
DB_NAME="gestion_conserjeria"
DB_ADMIN_USER="adminuser"
DB_ADMIN_PASSWORD="TuPasswordSeguro123!"  # CAMBIAR
```

---

### Fase 2: Crear Recursos de Azure (10 min)

#### 2.1 Crear grupo de recursos
```bash
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

#### 2.2 Crear base de datos PostgreSQL
```bash
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER_NAME \
  --location $LOCATION \
  --admin-user $DB_ADMIN_USER \
  --admin-password $DB_ADMIN_PASSWORD \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 14 \
  --public-access 0.0.0.0-255.255.255.255 \
  --yes
```

#### 2.3 Crear base de datos dentro del servidor
```bash
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $DB_SERVER_NAME \
  --database-name $DB_NAME
```

#### 2.4 Habilitar SSL en PostgreSQL
```bash
az postgres flexible-server parameter set \
  --resource-group $RESOURCE_GROUP \
  --server-name $DB_SERVER_NAME \
  --name require_secure_transport \
  --value ON
```

#### 2.5 Obtener connection string
```bash
# Construir connection string
DB_HOST="${DB_SERVER_NAME}.postgres.database.azure.com"
CONNECTION_STRING="postgresql://${DB_ADMIN_USER}:${DB_ADMIN_PASSWORD}@${DB_HOST}:5432/${DB_NAME}?sslmode=require"

echo "Tu connection string:"
echo $CONNECTION_STRING
```

---

### Fase 3: Preparar y Subir Imagen Docker (15 min)

#### 3.1 Actualizar settings.py con configuración de producción
```python
# core/settings.py
# Asegúrate de tener esta configuración

import os
from pathlib import Path

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'tu-secret-key-por-defecto')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'gestion_conserjeria'),
        'USER': os.environ.get('DB_USER', 'adminuser'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
            'sslrootcert': '/app/DigiCertGlobalRootG2.crt.pem'
        }
    }
}
```

#### 3.2 Build imagen Docker
```bash
# Desde la raíz del proyecto
docker build -t ${DOCKER_HUB_USER}/gestion-conserjeria:latest .
```

#### 3.3 Push a Docker Hub
```bash
docker push ${DOCKER_HUB_USER}/gestion-conserjeria:latest
```

---

### Fase 4: Desplegar Container App (15 min)

#### 4.1 Crear Container Apps Environment
```bash
az containerapp env create \
  --name $ENV_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

#### 4.2 Crear Container App
```bash
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENV_NAME \
  --image ${DOCKER_HUB_USER}/gestion-conserjeria:latest \
  --target-port 8000 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 5 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars \
    SECRET_KEY=secretvaluefromkeyvault123 \
    DEBUG=False \
    ALLOWED_HOSTS=*.azurecontainerapps.io \
    DB_NAME=$DB_NAME \
    DB_USER=$DB_ADMIN_USER \
    DB_PASSWORD=$DB_ADMIN_PASSWORD \
    DB_HOST=$DB_HOST \
    DB_PORT=5432
```

#### 4.3 Obtener URL de la aplicación
```bash
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```

---

### Fase 5: Restaurar Base de Datos (10 min)

#### 5.1 Conectar a PostgreSQL y restaurar backup
```bash
# Opción 1: Desde tu máquina local
psql "$CONNECTION_STRING" < backup_db.sql

# Opción 2: Usando Azure CLI
az postgres flexible-server execute \
  --name $DB_SERVER_NAME \
  --admin-user $DB_ADMIN_USER \
  --admin-password $DB_ADMIN_PASSWORD \
  --database-name $DB_NAME \
  --file-path backup_db.sql
```

#### 5.2 Aplicar migraciones (si hay nuevas)
```bash
# Conectar al container y ejecutar
az containerapp exec \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --command "python manage.py migrate"
```

---

### Fase 6: Verificación (5 min)

#### 6.1 Verificar que la app está corriendo
```bash
# Obtener URL
APP_URL=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Tu aplicación está en: https://$APP_URL"

# Probar endpoint
curl -I https://$APP_URL
```

#### 6.2 Verificar logs
```bash
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --tail 50
```

#### 6.3 Verificar escalado
```bash
az containerapp revision list \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --output table
```

---

## 📊 Configuración de Alertas de Presupuesto

### Opción 1: Desde Azure Portal (Recomendada para principiantes)

1. Ve a **Azure Portal** → Busca "Cost Management"
2. Selecciona **Budgets** (Presupuestos)
3. Click en **+ Add**
4. Configura:
   - **Scope**: Tu suscripción o grupo de recursos
   - **Budget name**: "Presupuesto-Conserjeria"
   - **Reset period**: Monthly
   - **Amount**: $3 USD
5. En **Alert conditions**:
   - **Type**: Actual
   - **% of budget**: 80 (recibirás alerta en $2.40)
   - **Email**: Tu correo electrónico
6. Guarda

### Opción 2: Usando Azure CLI

```bash
# Crear presupuesto de $3 con alerta al 80%
az consumption budget create \
  --budget-name "presupuesto-conserjeria" \
  --category Cost \
  --amount 3 \
  --time-grain Monthly \
  --resource-group $RESOURCE_GROUP \
  --notifications \
    '{"enabled":true,"operator":"GreaterThan","threshold":80,"contactEmails":["tu-email@example.com"]}'
```

---

## 🗑️ Eliminación de Recursos

### Cuando termines la demo, elimina TODO para mantener costo en $0:

#### Opción 1: Eliminar grupo de recursos completo (Recomendada)
```bash
# Esto elimina TODO: BD, Container App, Environment, etc.
az group delete \
  --name $RESOURCE_GROUP \
  --yes \
  --no-wait
```

#### Opción 2: Eliminar recursos individualmente

```bash
# 1. Eliminar Container App
az containerapp delete \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --yes

# 2. Eliminar Container Environment
az containerapp env delete \
  --name $ENV_NAME \
  --resource-group $RESOURCE_GROUP \
  --yes

# 3. Eliminar PostgreSQL
az postgres flexible-server delete \
  --name $DB_SERVER_NAME \
  --resource-group $RESOURCE_GROUP \
  --yes

# 4. Eliminar grupo de recursos vacío
az group delete \
  --name $RESOURCE_GROUP \
  --yes
```

### ⏱️ Tiempo de eliminación: ~5-10 minutos

---

## 🔧 Troubleshooting

### Problema 1: Container App no inicia

**Síntomas**: App muestra error 500 o no responde

**Solución**:
```bash
# Ver logs
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --tail 100

# Verificar variables de entorno
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.template.containers[0].env
```

### Problema 2: Error de conexión a base de datos

**Síntomas**: "could not connect to server" o "SSL connection error"

**Solución**:
```bash
# Verificar que PostgreSQL está activo
az postgres flexible-server show \
  --name $DB_SERVER_NAME \
  --resource-group $RESOURCE_GROUP

# Verificar firewall
az postgres flexible-server firewall-rule list \
  --name $DB_SERVER_NAME \
  --resource-group $RESOURCE_GROUP

# Verificar certificado SSL está en la imagen
docker run --rm ${DOCKER_HUB_USER}/gestion-conserjeria:latest ls -la /app/*.pem
```

### Problema 3: App no escala a 0

**Síntomas**: Costos más altos de lo esperado

**Solución**:
```bash
# Verificar configuración de escalado
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.template.scale

# Actualizar si es necesario
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 0 \
  --max-replicas 5
```

### Problema 4: Imagen Docker no se encuentra

**Síntomas**: "ImagePullBackOff" o "image not found"

**Solución**:
```bash
# Verificar que la imagen existe en Docker Hub
docker pull ${DOCKER_HUB_USER}/gestion-conserjeria:latest

# Si la imagen es privada, agregar credenciales
az containerapp registry set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --server docker.io \
  --username $DOCKER_HUB_USER \
  --password $DOCKER_HUB_PASSWORD
```

---

## 💵 Estimación de Costos

### Costos Detallados por Servicio

#### 1. Azure Container Apps
- **Sin tráfico (min replicas: 0)**: $0.000112/vCPU-segundo + $0.000012/GB-segundo
- **Con 1 réplica activa 24/7**:
  - 0.5 vCPU × $0.000112 × 2,592,000 segundos/mes = ~$145
  - 1 GB RAM × $0.000012 × 2,592,000 segundos/mes = ~$31
  - **Total: ~$176/mes** (por eso min replicas: 0 es clave)
- **Con min replicas: 0 y uso ocasional**: **~$0.50-2/mes**

#### 2. PostgreSQL Flexible Server
- **Burstable B1ms (1 vCore, 2 GB RAM)**: 
  - Compute: ~$13/mes
  - Storage (32 GB): ~$1.28/mes
  - Backup: Incluido
  - **Total: ~$14-15/mes**

#### 3. Container Apps Environment
- Incluido con Container Apps sin costo adicional cuando min replicas: 0

#### 4. Docker Hub (Registry)
- **Repositorio público**: **$0/mes**
- Repositorio privado: $5/mes (no necesario para portafolio)

### Escenarios de Uso

| Escenario | Costo Mensual | Costo Diario |
|-----------|---------------|--------------|
| **Recursos eliminados (sin nada desplegado)** | **$0** | **$0** |
| **Solo Container App (BD eliminada)** | ~$0.50-1 | ~$0.02-0.03 |
| **Todo desplegado, sin tráfico** | ~$14-16 | ~$0.47-0.53 |
| **Todo desplegado, BD activa solo 1 día** | ~$1.50 | ~$0.50 |
| **Demo de 2 horas con BD** | ~$0.04 | - |

### ⚡ Estrategia Óptima para Portafolio:

```
1. Mantener todo eliminado: $0/mes
2. Cuando reclutador solicite demo:
   - Desplegar todo: 45-60 min
   - Costo de 1 día completo: ~$0.50
3. Después de la demo:
   - Eliminar recursos: 5 min
   - Volver a $0/mes
```

**Costo anual estimado con 5 demos**: ~$2.50/año

---

## 📝 Notas Adicionales

### Mejoras Futuras
- [ ] Script de automatización completo (Bicep/Terraform)
- [ ] CI/CD con GitHub Actions
- [ ] Usar Azure Key Vault para secrets
- [ ] Implementar Azure Front Door para CDN
- [ ] Monitoreo con Application Insights

### Recursos Útiles
- [Documentación Azure Container Apps](https://docs.microsoft.com/azure/container-apps/)
- [Documentación PostgreSQL Flexible](https://docs.microsoft.com/azure/postgresql/flexible-server/)
- [Docker Hub](https://hub.docker.com/)
- [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)

---

## 🎓 Lecciones Aprendidas

1. **Min replicas: 0 es clave** para mantener costos bajos en portafolios
2. **Docker Hub gratuito** es suficiente para proyectos de demostración
3. **PostgreSQL Flexible** es el tier más económico, pero aún costoso para portafolios
4. **Eliminar recursos** después de cada demo es la mejor estrategia de costos
5. **Backup de BD** es esencial para poder recrear el ambiente rápidamente

---

**Versión**: 2.0  
**Última actualización**: Diciembre 2025  
**Autor**: Javier Castro  
**Repositorio**: [GitHub](https://github.com/cocoup1/Gestion-Conserjeria)
