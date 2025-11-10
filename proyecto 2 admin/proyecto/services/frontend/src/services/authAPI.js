import axios from 'axios';

const API_BASE = '/api/auth';

const authClient = axios.create({
  baseURL: API_BASE,
});

// Interceptor para añadir el token a las peticiones
authClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores 401 y desloguear al usuario
authClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

class AuthAPI {
  async login(identifier, password, loginType = "email") {
    try {
      console.log('🌐 authAPI.login() llamado con:', { identifier, loginType });
      const response = await authClient.post('/token', {
        identifier,
        password,
        login_type: loginType
      });
      console.log('🌐 Respuesta del servidor:', response.data);
      if (response.data.access_token) {
        console.log('💾 Guardando token en localStorage...');

        // Limpiar sesión de chatbot anterior antes de guardar el nuevo token
        localStorage.removeItem('chatbot_session_id');
        localStorage.removeItem('chatbot_messages');

        localStorage.setItem('authToken', response.data.access_token);
        console.log('💾 Token guardado exitosamente');
      }
      return response.data;
    } catch (error) {
      console.error('❌ Error during login:', error.response?.data || error.message);
      throw error;
    }
  }

  async register(userData) {
    try {
      const userDataWithRole = {
        ...userData,
        rool: "user"
      }
      // userData debe contener: { email, nombre, rut, password }
      const response = await authClient.post('/register', userData);
      if (response.data.access_token) {
        localStorage.setItem('authToken', response.data.access_token);
      }
      return response.data;
    } catch (error) {
      console.error('Error during registration:', error.response?.data || error.message);
      throw error;
    }
  }

  logout() {
    // Limpiar token de autenticación
    localStorage.removeItem('authToken');
    localStorage.removeItem('token'); // Por si se usa este nombre en algún lugar

    // Limpiar sesión del chatbot
    localStorage.removeItem('chatbot_session_id');
    localStorage.removeItem('chatbot_messages');
    localStorage.removeItem('chatbot_user'); // 👈 Nuevo: Limpiar usuario del chatbot

    // Redirigir al login
    window.location.href = '/login';
  }

  isAuthenticated() {
    return !!localStorage.getItem('authToken');
  }

  async getCurrentUser() {
    try {
      const response = await authClient.get('/users/me');
      return response.data;
    } catch (error) {
      console.error('Error fetching current user:', error);
      // El interceptor de respuesta se encargará de redirigir si es un 401
      throw error;
    }
  }

  async getUsers() {
    try {
      const response = await authClient.get('/users');
      return response.data;
    } catch (error) {
      console.error('Error fetching users:', error);
      throw error;
    }
  }

  // Principio de Responsabilidad Única: función especializada para registro de empleados
  async registerEmployee(employeeData) {
    try {
      const response = await authClient.post('/admin/employees', employeeData);
      return response.data;
    } catch (error) {
      console.error('Error registering employee:', error.response?.data || error.message);
      throw error;
    }
  }

  // Función para obtener el token (útil para llamadas directas)
  getToken() {
    return localStorage.getItem('authToken');
  }

  // 📧 Funciones de recuperación de contraseña
  async requestPasswordReset(email) {
    try {
      const response = await authClient.post('/password-reset/request', {
        email: email
      });
      return response.data;
    } catch (error) {
      console.error('Error solicitando recuperación de contraseña:', error.response?.data || error.message);
      throw error;
    }
  }

  async confirmPasswordReset(token, newPassword) {
    try {
      const response = await authClient.post('/password-reset/confirm', {
        token: token,
        new_password: newPassword
      });
      return response.data;
    } catch (error) {
      console.error('Error confirmando nueva contraseña:', error.response?.data || error.message);
      throw error;
    }
  }
}

export default new AuthAPI();
