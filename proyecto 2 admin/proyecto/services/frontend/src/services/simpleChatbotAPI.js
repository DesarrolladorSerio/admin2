import axios from 'axios';

const apiClient = axios.create({
    baseURL: '/api/chatbot'
});

class SimpleChatBotAPI {
    /**
     * Enviar mensaje al chatbot
     * @param {string} message - Mensaje del usuario  
     * @param {string} sessionId - ID de la sesión
     */
    async sendMessage(message, sessionId = null) {
        try {
            console.log('🤖 SimpleChatBotAPI - Enviando mensaje (autenticado)');

            // Obtener el token de autenticación
            const token = localStorage.getItem('authToken') || localStorage.getItem('token');

            if (!token) {
                throw new Error('No hay token de autenticación');
            }

            const response = await apiClient.post('/chat', {
                message: message,
                session_id: sessionId
            }, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });

            return {
                response: response.data.response || 'Lo siento, no pude procesar tu consulta.',
                session_id: response.data.session_id || sessionId
            };
        } catch (error) {
            console.error('Error enviando mensaje al chatbot:', error);

            // Manejar error de autenticación
            if (error.response?.status === 401) {
                throw new Error('Debes iniciar sesión para usar el chatbot');
            }

            // Si el servicio no está disponible
            if (error.response?.status >= 500 || error.code === 'ECONNREFUSED') {
                return {
                    response: '🤖 El servicio de IA no está disponible en este momento. Por favor, intenta más tarde o contacta al administrador.',
                    session_id: sessionId || 'fallback-session'
                };
            }

            throw error;
        }
    }

    /**
     * Obtener historial de la sesión (simulado para compatibilidad)
     */
    async getSessionHistory(sessionId) {
        // Por ahora retornamos un array vacío ya que Ollama no mantiene historial de sesiones
        return {
            messages: [],
            session_id: sessionId
        };
    }

    /**
     * Limpiar historial (simulado para compatibilidad)
     */
    async clearHistory(sessionId) {
        return {
            success: true,
            message: 'Historial limpiado (simulado)',
            session_id: sessionId
        };
    }

    /**
     * Verificar estado del servicio
     */
    async checkHealth() {
        try {
            const response = await apiClient.get('/health');
            return {
                status: 'ok',
                service: 'chatbot-ai',
                message: 'Servicio de chatbot disponible'
            };
        } catch (error) {
            console.error('Error verificando estado del chatbot:', error);
            return {
                status: 'error',
                service: 'chatbot-ai',
                message: 'Error al verificar el servicio de chatbot'
            };
        }
    }

    /**
     * Obtener métricas (simulado para compatibilidad)
     */
    async getMetrics() {
        return {
            total_messages: 0,
            active_sessions: 1,
            model: 'phi3.5',
            status: 'simplified-version'
        };
    }

    /**
     * Obtener sesiones del usuario (simulado para compatibilidad)
     */
    async getUserSessions() {
        return {
            sessions: [{
                id: 'ollama-session-' + Date.now(),
                created_at: new Date().toISOString(),
                last_message: new Date().toISOString(),
                message_count: 0
            }]
        };
    }
}

export default new SimpleChatBotAPI();