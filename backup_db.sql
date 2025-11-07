-- Script para hacer backup y cambiar nombres de columnas
-- Base de datos: conserjeria_4
-- Fecha: 2025-11-06

-- PASO 1: BACKUP (ejecutar primero para guardar datos)
-- mysqldump -u root -p conserjeria_4 > backup_conserjeria_$(date +%Y%m%d).sql

-- PASO 2: Verificar nombres actuales de columnas
SELECT COLUMN_NAME, DATA_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'conserjeria_4' 
  AND TABLE_NAME = 'authentication_empleados' 
  AND COLUMN_NAME IN ('id_region_id', 'id_comuna_id');

-- PASO 3: Renombrar columnas en authentication_empleados
ALTER TABLE `authentication_empleados` 
  CHANGE `id_region_id` `region_id` bigint(20) NOT NULL,
  CHANGE `id_comuna_id` `comuna_id` bigint(20) NOT NULL;

-- PASO 4: Verificar que el cambio se aplicó correctamente
SELECT COLUMN_NAME, DATA_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'conserjeria_4' 
  AND TABLE_NAME = 'authentication_empleados' 
  AND COLUMN_NAME IN ('region_id', 'comuna_id');

-- PASO 5: Verificar que las claves foráneas aún funcionan
SELECT 
    e.rut,
    e.nombres,
    r.nombre as region,
    c.nombre as comuna
FROM authentication_empleados e
LEFT JOIN authentication_region r ON e.region_id = r.id
LEFT JOIN authentication_comuna c ON e.comuna_id = c.id
LIMIT 5;
