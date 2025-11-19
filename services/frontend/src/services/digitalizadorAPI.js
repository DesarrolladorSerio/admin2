import axios from 'axios';

// Usar rutas relativas que se resuelven a través del proxy nginx
const API_BASE = '/api/documents';

/**
 * Servicio API para el módulo de Digitalizador
 * Maneja todas las operaciones de digitalización (RF14-RF18)
 */

// Configuración de axios con token
const getAuthHeaders = () => {
    const token = localStorage.getItem('authToken');
    return {
        headers: {
            Authorization: `Bearer ${token}`
        }
    };
};

const getAuthHeadersJSON = () => {
    const token = localStorage.getItem('authToken');
    return {
        headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    };
};

// =============================================================================
// RF14-RF15: DIGITALIZACIÓN DE DOCUMENTOS
// =============================================================================

/**
 * Subir documento ciudadano (nuevo - con reserva)
 */
export const subirDocumentoCiudadano = async (file, reservaId, tipoDocumento) => {
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        // Solo agregar reserva_id si tiene un valor válido
        if (reservaId && reservaId !== '' && !isNaN(reservaId)) {
            formData.append('reserva_id', parseInt(reservaId));
        }
        
        // Solo agregar tipo_documento si tiene un valor válido
        if (tipoDocumento && tipoDocumento.trim() !== '') {
            formData.append('tipo_documento', tipoDocumento.trim());
        }

        const response = await axios.post(
            `${API_BASE}/upload-documento`,
            formData,
            {
                headers: {
                    ...getAuthHeaders().headers,
                    'Content-Type': 'multipart/form-data'
                }
            }
        );
        return response.data;
    } catch (error) {
        console.error('Error al subir documento ciudadano:', error);
        throw error;
    }
};

/**
 * Subir documento antiguo del archivo
 */
export const subirDocumentoAntiguo = async (file, datosDocumento) => {
    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('numero_expediente', datosDocumento.numero_expediente);
        formData.append('tipo_tramite', datosDocumento.tipo_tramite);
        formData.append('año_tramite', datosDocumento.año_tramite);
        formData.append('descripcion', datosDocumento.descripcion);
        formData.append('numero_fojas', datosDocumento.numero_fojas || 1);

        if (datosDocumento.ciudadano_rut) {
            formData.append('ciudadano_rut', datosDocumento.ciudadano_rut);
        }
        if (datosDocumento.ciudadano_nombre) {
            formData.append('ciudadano_nombre', datosDocumento.ciudadano_nombre);
        }
        if (datosDocumento.palabras_clave) {
            formData.append('palabras_clave', datosDocumento.palabras_clave);
        }
        if (datosDocumento.ubicacion_fisica) {
            formData.append('ubicacion_fisica', datosDocumento.ubicacion_fisica);
        }

        const response = await axios.post(
            `${API_BASE}/documentos-antiguos`,
            formData,
            {
                headers: {
                    ...getAuthHeaders().headers,
                    'Content-Type': 'multipart/form-data'
                }
            }
        );
        return response.data;
    } catch (error) {
        console.error('Error al subir documento antiguo:', error);
        throw error;
    }
};

/**
 * Marcar documento antiguo como completado
 */
export const completarDigitalizacion = async (docId, calidad, notas = '') => {
    try {
        const response = await axios.put(
            `${API_BASE}/documentos-antiguos/${docId}/completar`,
            null,
            {
                ...getAuthHeadersJSON(),
                params: { calidad, notas }
            }
        );
        return response.data;
    } catch (error) {
        console.error('Error al completar digitalización:', error);
        throw error;
    }
};

// =============================================================================
// RF16: CATALOGACIÓN Y BÚSQUEDA
// =============================================================================

/**
 * Buscar documentos antiguos
 */
export const buscarDocumentosAntiguos = async (filtros) => {
    try {
        const response = await axios.post(
            `${API_BASE}/documentos-antiguos/buscar`,
            filtros,
            getAuthHeadersJSON()
        );
        return response.data;
    } catch (error) {
        console.error('Error en búsqueda de documentos:', error);
        throw error;
    }
};

/**
 * Obtener documentos pendientes de digitalizar
 */
export const getDocumentosPendientes = async (limit = 50) => {
    try {
        const response = await axios.get(
            `${API_BASE}/documentos-antiguos/pendientes`,
            {
                ...getAuthHeaders(),
                params: { limit }
            }
        );
        return response.data;
    } catch (error) {
        console.error('Error al obtener documentos pendientes:', error);
        throw error;
    }
};

/**
 * Obtener documentos de una reserva
 */
export const getDocumentosReserva = async (reservaId) => {
    try {
        const response = await axios.get(
            `${API_BASE}/documentos/reserva/${reservaId}`,
            getAuthHeaders()
        );
        return response.data;
    } catch (error) {
        console.error('Error al obtener documentos de reserva:', error);
        throw error;
    }
};

/**
 * Obtener todos los documentos de un usuario
 */
export const getDocumentosUsuario = async (usuarioId) => {
    try {
        const response = await axios.get(
            `${API_BASE}/documentos/usuario/${usuarioId}`,
            getAuthHeaders()
        );
        return response.data;
    } catch (error) {
        console.error('Error al obtener los documentos del usuario:', error);
        throw error;
    }
};

/**
 * Revisar documento ciudadano
 */
export const revisarDocumento = async (documentoId, estado, notas = '') => {
    try {
        const response = await axios.put(
            `${API_BASE}/documentos/${documentoId}/revisar`,
            {
                estado, // aprobado, rechazado
                notas
            },
            getAuthHeadersJSON()
        );
        return response.data;
    } catch (error) {
        console.error('Error al revisar documento:', error);
        throw error;
    }
};

// =============================================================================
// RF14 y RF18: REGISTRO DE JORNADAS Y REPORTES
// =============================================================================

/**
 * Registrar jornada de digitalización
 */
export const registrarJornada = async (datosJornada) => {
    try {
        const response = await axios.post(
            `${API_BASE}/registro-digitalizacion`,
            datosJornada,
            getAuthHeadersJSON()
        );
        return response.data;
    } catch (error) {
        console.error('Error al registrar jornada:', error);
        throw error;
    }
};

/**
 * Obtener reporte diario
 */
export const getReporteDiario = async (fecha) => {
    try {
        const response = await axios.get(
            `${API_BASE}/reportes/digitalizacion/diario`,
            {
                ...getAuthHeaders(),
                params: { fecha }
            }
        );
        return response.data;
    } catch (error) {
        console.error('Error al obtener reporte diario:', error);
        throw error;
    }
};

/**
 * Obtener reporte semanal
 */
export const getReporteSemanal = async (fechaInicio) => {
    try {
        const response = await axios.get(
            `${API_BASE}/reportes/digitalizacion/semanal`,
            {
                ...getAuthHeaders(),
                params: { fecha_inicio: fechaInicio }
            }
        );
        return response.data;
    } catch (error) {
        console.error('Error al obtener reporte semanal:', error);
        throw error;
    }
};

/**
 * Obtener reporte mensual
 */
export const getReporteMensual = async (año, mes) => {
    try {
        const response = await axios.get(
            `${API_BASE}/reportes/digitalizacion/mensual`,
            {
                ...getAuthHeaders(),
                params: { año, mes }
            }
        );
        return response.data;
    } catch (error) {
        console.error('Error al obtener reporte mensual:', error);
        throw error;
    }
};

/**
 * Obtener avance general de digitalización antigua
 */
export const getAvanceDigitalizacion = async () => {
    try {
        const response = await axios.get(
            `${API_BASE}/reportes/avance-antiguos`,
            getAuthHeaders()
        );
        return response.data;
    } catch (error) {
        console.error('Error al obtener avance de digitalización:', error);
        throw error;
    }
};

// =============================================================================
// UTILIDADES
// =============================================================================

/**
 * Tipos de documentos disponibles
 */
export const TIPOS_DOCUMENTO = {
    cedula: 'Cédula de Identidad',
    certificado_medico: 'Certificado Médico',
    foto: 'Fotografía',
    antecedentes: 'Certificado de Antecedentes',
    comprobante_domicilio: 'Comprobante de Domicilio',
    licencia_anterior: 'Licencia Anterior',
    certificado_estudio: 'Certificado de Estudios',
    otro: 'Otro'
};

/**
 * Calidades de digitalización
 */
export const CALIDADES = {
    baja: 'Baja (legible con dificultad)',
    media: 'Media (legible)',
    alta: 'Alta (excelente calidad)'
};

export default {
    subirDocumentoCiudadano,
    subirDocumentoAntiguo,
    completarDigitalizacion,
    buscarDocumentosAntiguos,
    getDocumentosPendientes,
    getDocumentosReserva,
    getDocumentosUsuario,
    revisarDocumento,
    registrarJornada,
    getReporteDiario,
    getReporteSemanal,
    getReporteMensual,
    getAvanceDigitalizacion,
    TIPOS_DOCUMENTO,
    CALIDADES
};
