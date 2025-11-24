INSERT INTO documentos_ciudadano (reserva_id, usuario_id, usuario_rut, tipo_documento, nombre_archivo, ruta_archivo, tamano_bytes, mime_type, estado, fecha_carga) 
VALUES 
    (1, 1, '11111111-1', 'certificado_residencia', 'certificado_admin.pdf', '/uploads/certificado_admin.pdf', 1024, 'application/pdf', 'pendiente', NOW()),
    (2, 1, '11111111-1', 'licencia_conducir', 'licencia_admin.pdf', '/uploads/licencia_admin.pdf', 2048, 'application/pdf', 'aprobado', NOW() - INTERVAL '1 day');