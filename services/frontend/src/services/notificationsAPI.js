import axios from 'axios';

// Cliente axios para el servicio de notificaciones
const notificationsClient = axios.create({
    baseURL: '/api/notifications',
    headers: {
        'Content-Type': 'application/json'
    },
    timeout: 30000 // 30 segundos
});

// Interceptor para agregar token si existe
notificationsClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// API de notificaciones
const notificationsAPI = {
    /**
     * Enviar email genérico
     */
    sendEmail: async (emailData) => {
        try {
            const response = await notificationsClient.post('/email', emailData);
            return response.data;
        } catch (error) {
            console.error('Error enviando email:', error);
            throw error;
        }
    },

    /**
     * Enviar confirmación de reserva
     */
    sendReservationConfirmation: async (reservationData) => {
        try {
            const response = await notificationsClient.post(
                '/reservation/confirmation',
                reservationData
            );
            return response.data;
        } catch (error) {
            console.error('Error enviando confirmación de reserva:', error);
            throw error;
        }
    },

    /**
     * Enviar recordatorio de reserva
     */
    sendReservationReminder: async (reservationData) => {
        try {
            const response = await notificationsClient.post(
                '/reservation/reminder',
                reservationData
            );
            return response.data;
        } catch (error) {
            console.error('Error enviando recordatorio:', error);
            throw error;
        }
    },

    /**
     * Enviar notificación de cancelación
     */
    sendReservationCancellation: async (reservationData) => {
        try {
            const response = await notificationsClient.post(
                '/reservation/cancellation',
                reservationData
            );
            return response.data;
        } catch (error) {
            console.error('Error enviando cancelación:', error);
            throw error;
        }
    },

    /**
     * Enviar notificación de documento
     */
    sendDocumentNotification: async (documentData) => {
        try {
            const response = await notificationsClient.post(
                '/document',
                documentData
            );
            return response.data;
        } catch (error) {
            console.error('Error enviando notificación de documento:', error);
            throw error;
        }
    },

    /**
     * Enviar email de bienvenida
     */
    sendWelcomeEmail: async (userData) => {
        try {
            const response = await notificationsClient.post('/welcome', userData);
            return response.data;
        } catch (error) {
            console.error('Error enviando email de bienvenida:', error);
            throw error;
        }
    },

    /**
     * Enviar email de recuperación de contraseña
     */
    sendPasswordReset: async (resetData) => {
        try {
            const response = await notificationsClient.post(
                '/password-reset',
                resetData
            );
            return response.data;
        } catch (error) {
            console.error('Error enviando recuperación de contraseña:', error);
            throw error;
        }
    },

    /**
     * Enviar lote de emails
     */
    sendBatchEmails: async (emailsArray) => {
        try {
            const response = await notificationsClient.post('/batch', {
                emails: emailsArray
            });
            return response.data;
        } catch (error) {
            console.error('Error enviando lote de emails:', error);
            throw error;
        }
    },

    /**
     * Consultar estado de una tarea
     */
    getTaskStatus: async (taskId) => {
        try {
            const response = await notificationsClient.get(`/task/${taskId}`);
            return response.data;
        } catch (error) {
            console.error('Error consultando estado de tarea:', error);
            throw error;
        }
    },

    /**
     * Obtener estadísticas del servicio
     */
    getStats: async () => {
        try {
            const response = await notificationsClient.get('/stats');
            return response.data;
        } catch (error) {
            console.error('Error obteniendo estadísticas:', error);
            throw error;
        }
    }
};

export default notificationsAPI;
