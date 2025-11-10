import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost';

/**
 * Servicio API para el módulo de Administrador
 * Maneja todas las operaciones administrativas (RF08-RF13)
 */

// Configuración de axios con token
const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
        headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    };
};

// =============================================================================
// RF08: DASHBOARD ADMINISTRATIVO
// =============================================================================

/**
 * Obtener dashboard con estadísticas y listado de reservas
 */
export const getDashboard = async () => {
    try {
        const response = await axios.get(
            `${API_URL}/api/reservations/admin/dashboard`,
            getAuthHeaders()
        );
        return response.data;
    } catch (error) {
        console.error('Error al obtener dashboard:', error);
        throw error;
    }
};

/**
 * Actualizar estado documental de una reserva
 */
export const actualizarEstadoDocumental = async (reservaId, estado, notasAdmin = '') => {
    try {
        const response = await axios.put(
            `${API_URL}/api/reservations/admin/actualizar-estado-documental/${reservaId}`,
            {
                estado_documental: estado, // pendiente, incompleto, completo
                notas_admin: notasAdmin
            },
            getAuthHeaders()
        );
        return response.data;
    } catch (error) {
        console.error('Error al actualizar estado documental:', error);
        throw error;
    }
};

// =============================================================================
// RF09: BÚSQUEDAS Y CONSULTAS AVANZADAS
// =============================================================================

/**
 * Búsqueda avanzada de reservas
 */
export const buscarReservas = async (filtros) => {
    try {
        const response = await axios.post(
            `${API_URL}/api/reservations/admin/buscar-reservas`,
            filtros,
            getAuthHeaders()
        );
        return response.data;
    } catch (error) {
        console.error('Error en búsqueda avanzada:', error);
        throw error;
    }
};

/**
 * Obtener estadísticas y rankings por tipo de trámite
 */
export const getEstadisticasTramites = async (fechaInicio = null, fechaFin = null) => {
    try {
        const params = {};
        if (fechaInicio) params.fecha_inicio = fechaInicio;
        if (fechaFin) params.fecha_fin = fechaFin;

        const response = await axios.get(
            `${API_URL}/api/reservations/admin/estadisticas-tramites`,
            {
                ...getAuthHeaders(),
                params
            }
        );
        return response.data;
    } catch (error) {
        console.error('Error al obtener estadísticas:', error);
        throw error;
    }
};

// =============================================================================
// RF10: NOTIFICACIONES AL CIUDADANO
// =============================================================================

/**
 * Enviar notificación a ciudadano
 */
export const enviarNotificacion = async (reservaId, tipo, mensaje) => {
    try {
        const response = await axios.post(
            `${API_URL}/api/reservations/admin/enviar-notificacion/${reservaId}`,
            {
                tipo, // recordatorio, documentos_faltantes, anulacion
                mensaje
            },
            getAuthHeaders()
        );
        return response.data;
    } catch (error) {
        console.error('Error al enviar notificación:', error);
        throw error;
    }
};

// =============================================================================
// RF12: VENCIMIENTOS DE LICENCIAS
// =============================================================================

/**
 * Consultar licencias próximas a vencer
 */
export const getVencimientosProximos = async (dias = 30) => {
    try {
        const response = await axios.get(
            `${API_URL}/api/reservations/admin/vencimientos-proximos`,
            {
                ...getAuthHeaders(),
                params: { dias }
            }
        );
        return response.data;
    } catch (error) {
        console.error('Error al consultar vencimientos:', error);
        throw error;
    }
};

/**
 * Obtener licencias por vencer desde auth service
 */
export const getLicenciasPorVencer = async (dias = 30) => {
    try {
        const response = await axios.get(
            `${API_URL}/api/auth/admin/licencias-por-vencer`,
            {
                ...getAuthHeaders(),
                params: { dias }
            }
        );
        return response.data;
    } catch (error) {
        console.error('Error al consultar licencias por vencer:', error);
        throw error;
    }
};

// =============================================================================
// RF13: ANULACIÓN DE RESERVAS
// =============================================================================

/**
 * Anular una reserva con motivo
 */
export const anularReserva = async (reservaId, motivo) => {
    try {
        const response = await axios.post(
            `${API_URL}/api/reservations/admin/anular-reserva/${reservaId}`,
            { motivo },
            getAuthHeaders()
        );
        return response.data;
    } catch (error) {
        console.error('Error al anular reserva:', error);
        throw error;
    }
};

// =============================================================================
// UTILIDADES
// =============================================================================

/**
 * Obtener todas las reservas detalladas
 */
export const getAllReservations = async () => {
    try {
        const response = await axios.get(
            `${API_URL}/api/reservations/admin/reservations`,
            getAuthHeaders()
        );
        return response.data;
    } catch (error) {
        console.error('Error al obtener reservas:', error);
        throw error;
    }
};

/**
 * Exportar datos a CSV (del lado del cliente)
 */
export const exportarCSV = (datos, nombreArchivo) => {
    const headers = Object.keys(datos[0] || {});
    const csv = [
        headers.join(','),
        ...datos.map(row => headers.map(field => JSON.stringify(row[field] || '')).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${nombreArchivo}.csv`;
    link.click();
};

export default {
    getDashboard,
    actualizarEstadoDocumental,
    buscarReservas,
    getEstadisticasTramites,
    enviarNotificacion,
    getVencimientosProximos,
    getLicenciasPorVencer,
    anularReserva,
    getAllReservations,
    exportarCSV
};
