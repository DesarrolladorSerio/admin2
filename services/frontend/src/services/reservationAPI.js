import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api/reservations'
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

class ReservationAPI {
  async getReservations() {
    const response = await apiClient.get('/reservations');
    return response.data;
  }

  async getReservationsByDateRange(startDate, endDate) {
    const response = await apiClient.get(`/reservations/calendar/${startDate}/${endDate}`);
    return response.data;
  }

  async createReservation(reservationData) {
    const response = await apiClient.post('/reservations', reservationData);
    return response.data;
  }

  async updateReservation(id, updateData) {
    const response = await apiClient.put(`/reservations/${id}`, updateData);
    return response.data;
  }

  async deleteReservation(id, reason) {
    const response = await apiClient.delete(`/reservations/${id}`, {
      data: { reason: reason }
    });
    return response.data;
  }

  async getReservation(id) {
    const response = await apiClient.get(`/reservations/${id}`);
    return response.data;
  }

  async getTiposTramites() {
    const response = await apiClient.get('/tipos-tramites');
    return response.data;
  }

  async checkAvailability(fecha, hora, tipoTramite, reservationId = null) {
    const params = reservationId ? `?reservation_id=${reservationId}` : '';
    const response = await apiClient.get(`/check-availability/${fecha}/${hora}/${tipoTramite}${params}`);
    return response.data;
  }

  /**
   * 🔍 RF05: Valida si el usuario cumple los requisitos para un tipo de trámite
   * @param {string} tipoTramite - ID del tipo de trámite
   * @param {number} userId - ID del usuario (opcional)
   * @returns {Promise<Object>} Resultado de validación con bloqueantes, advertencias, documentos, etc.
   */
  async validarRequisitos(tipoTramite, userId = null) {
    const token = localStorage.getItem('authToken');
    const response = await apiClient.post('/validar-requisitos-tramite', {
      tipo_tramite: tipoTramite,
      user_id: userId,
      token: token
    });
    return response.data;
  }

  // Método específico para admin/empleados
  async getAllReservationsDetailed() {
    const response = await apiClient.get('/admin/reservations');
    return response.data;
  }
}

export default new ReservationAPI();
