import axios from 'axios';

const API_BASE = '/api/reservations';

const adminClient = axios.create({
  baseURL: API_BASE,
});

// Interceptor to add the token to requests
adminClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor to handle 401 errors and log out the user
adminClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

class AdminAPI {
  async getDashboardData() {
    try {
      const response = await adminClient.get('/admin/dashboard');
      return response.data;
    } catch (error) {
      console.error('Error fetching admin dashboard data:', error.response?.data || error.message);
      throw error;
    }
  }

  async getTramiteStats(startDate = null, endDate = null) {
    try {
      const params = {};
      if (startDate) params.fecha_inicio = startDate;
      if (endDate) params.fecha_fin = endDate;
      
      const response = await adminClient.get('/admin/estadisticas-tramites', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching tramite stats:', error.response?.data || error.message);
      throw error;
    }
  }

  async buscarReservas(searchCriteria) {
    try {
      const response = await adminClient.post('/admin/buscar-reservas', searchCriteria);
      return response.data;
    } catch (error) {
      console.error('Error searching reservations:', error.response?.data || error.message);
      throw error;
    }
  }
}

export default new AdminAPI();