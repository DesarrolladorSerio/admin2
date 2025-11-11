import axios from 'axios';

const apiClient = axios.create({
    baseURL: '/api/chatbot'
});

// Interceptor para añadir el token de autenticación a todas las peticiones
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Interceptor para manejar errores de autenticación
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('authToken');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

class ChatBotAPI {
    /**
     * Enviar mensaje al chatbot
     * @param {string} message - Mensaje del usuario
     * @param {string} sessionId - ID de la sesión (opcional)
     * @param {boolean} forceNewSession - Forzar creación de nueva conversación
     */
    async sendMessage(message, sessionId = null, forceNewSession = false) {
        try {
            const response = await apiClient.post('/chat', {
                message: message,
                session_id: sessionId,
                force_new_session: forceNewSession
            });
            return response.data;
        } catch (error) {
            console.error('Error enviando mensaje al chatbot:', error);
            throw error;
        }
    }

    /**
     * Obtener historial de una sesión
     * @param {string} sessionId - ID de la sesión
     */
    async getSessionHistory(sessionId) {
        try {
            const response = await apiClient.get(`/sessions?session_id=${sessionId}`);
            return response.data;
        } catch (error) {
            console.error('Error obteniendo historial de sesión:', error);
            throw error;
        }
    }

    /**
     * Eliminar una sesión de chat
     * @param {string} sessionId - ID de la sesión
     */
    async deleteSession(sessionId) {
        try {
            const response = await apiClient.delete(`/chat/session/${sessionId}`);
            return response.data;
        } catch (error) {
            console.error('Error eliminando sesión:', error);
            throw error;
        }
    }

    /**
     * Obtener métricas del chatbot
     */
    async getMetrics() {
        try {
            const response = await apiClient.get('/chat/metrics');
            return response.data;
        } catch (error) {
            console.error('Error obteniendo métricas:', error);
            throw error;
        }
    }

    /**
     * Obtener todas las conversaciones del usuario con preview
     * Similar al historial de ChatGPT
     */
    async getConversations() {
        try {
            const response = await apiClient.get('/chat/conversations');
            return response.data;
        } catch (error) {
            console.error('Error obteniendo conversaciones:', error);
            throw error;
        }
    }

    /**
     * Crear una nueva conversación
     * @param {string} initialMessage - Mensaje inicial (opcional)
     */
    async createNewConversation(initialMessage = "Hola") {
        try {
            const response = await apiClient.post('/chat', {
                message: initialMessage,
                force_new_session: true
            });
            return response.data;
        } catch (error) {
            console.error('Error creando nueva conversación:', error);
            throw error;
        }
    }

    /**
     * Cargar mensajes de una conversación específica
     * @param {string} sessionId - ID de la sesión
     */
    async loadConversation(sessionId) {
        try {
            const response = await apiClient.get(`/sessions?session_id=${sessionId}`);
            return response.data;
        } catch (error) {
            console.error('Error cargando conversación:', error);
            throw error;
        }
    }

    /**
     * Obtener todas las sesiones del usuario (deprecado, usar getConversations)
     */
    async getUserSessions() {
        try {
            const response = await apiClient.get('/chat/sessions');
            return response.data;
        } catch (error) {
            console.error('Error obteniendo sesiones del usuario:', error);
            throw error;
        }
    }

    /**
     * Verificar estado del servicio de chatbot
     */
    async checkHealth() {
        try {
            const response = await apiClient.get('/health');
            return response.data;
        } catch (error) {
            console.error('Error verificando estado del chatbot:', error);
            throw error;
        }
    }
}

export default new ChatBotAPI();