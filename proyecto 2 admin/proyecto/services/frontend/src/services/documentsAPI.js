import axios from 'axios';

const apiClient = axios.create({
    baseURL: '/api/documents'
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

class DocumentsAPI {
    /**
     * Obtener lista de documentos del usuario
     */
    async getDocuments() {
        const response = await apiClient.get('/my-documents');
        return response.data;
    }

    /**
     * Obtener tipos de documentos disponibles
     */
    async getDocumentTypes() {
        const response = await apiClient.get('/document-types');
        return response.data;
    }

    /**
     * Subir un nuevo documento
     * @param {File} file - Archivo a subir
     * @param {string} title - Título del documento
     * @param {string} description - Descripción del documento
     * @param {string} documentType - Nombre del tipo de documento (cedula, licencia_conducir, etc)
     * @param {Array} tags - Array de tags/etiquetas
     */
    async uploadDocument(file, title, description, documentType, tags = []) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('document_type', documentType);

        if (title) {
            formData.append('title', title);
        }
        if (description) {
            formData.append('description', description);
        }

        // Convertir tags a string separado por comas
        if (tags && tags.length > 0) {
            formData.append('tags', tags.join(','));
        }

        const response = await apiClient.post('/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            // Callback para progreso de subida (opcional)
            onUploadProgress: (progressEvent) => {
                const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                console.log(`Upload Progress: ${percentCompleted}%`);
            }
        });
        return response.data;
    }

    /**
     * Descargar un documento
     * @param {number} documentId - ID del documento
     */
    async downloadDocument(documentId) {
        const response = await apiClient.get(`/download/${documentId}`, {
            responseType: 'blob' // Importante para archivos binarios
        });

        // Crear URL de descarga
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;

        // Intentar obtener el nombre del archivo del header
        const contentDisposition = response.headers['content-disposition'];
        let filename = `document_${documentId}`;
        if (contentDisposition && contentDisposition.includes('filename=')) {
            filename = contentDisposition.split('filename=')[1].replace(/"/g, '');
        }

        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        return response;
    }

    /**
     * Obtener información de un documento específico
     * @param {number} documentId - ID del documento
     */
    async getDocument(documentId) {
        const response = await apiClient.get(`/documents/${documentId}`);
        return response.data;
    }

    /**
     * Eliminar un documento
     * @param {number} documentId - ID del documento
     */
    async deleteDocument(documentId) {
        const response = await apiClient.delete(`/documents/${documentId}`);
        return response.data;
    }

    /**
     * Actualizar metadatos de un documento
     * @param {number} documentId - ID del documento
     * @param {Object} updateData - Datos a actualizar (title, description, tags)
     */
    async updateDocument(documentId, updateData) {
        const response = await apiClient.put(`/documents/${documentId}`, updateData);
        return response.data;
    }

    /**
     * Compartir un documento con otros usuarios
     * @param {number} documentId - ID del documento
     * @param {string} sharedWithEmail - Email del usuario con quien compartir
     * @param {string} permission - Tipo de permiso ('read' o 'write')
     */
    async shareDocument(documentId, sharedWithEmail, permission = 'read') {
        const response = await apiClient.post(`/documents/${documentId}/share`, {
            shared_with_email: sharedWithEmail,
            permission: permission
        });
        return response.data;
    }

    /**
     * Obtener documentos compartidos conmigo
     */
    async getSharedDocuments() {
        const response = await apiClient.get('/shared-with-me');
        return response.data;
    }

    /**
     * Buscar documentos por título, descripción o tags
     * @param {string} query - Término de búsqueda
     */
    async searchDocuments(query) {
        const response = await apiClient.get(`/search?q=${encodeURIComponent(query)}`);
        return response.data;
    }

    /**
     * Obtener estadísticas del usuario (total documentos, espacio usado, etc.)
     */
    async getStats() {
        const response = await apiClient.get('/stats');
        return response.data;
    }
}

export default new DocumentsAPI();