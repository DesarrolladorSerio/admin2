-- Script para agregar columnas faltantes a la tabla user
-- Ejecutar este script en auth_db para sincronizar con el modelo User

-- Agregar columnas telefono y direccion si no existen
ALTER TABLE "user" 
ADD COLUMN IF NOT EXISTS telefono VARCHAR,
ADD COLUMN IF NOT EXISTS direccion VARCHAR;

-- Verificar las columnas
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'user';
