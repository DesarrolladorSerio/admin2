import React, { useState, useEffect } from 'react';
import documentsAPI from '../services/documentsAPI';

const DocumentsComponent = () => {
    const [documents, setDocuments] = useState([]);
    const [documentTypes, setDocumentTypes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadForm, setUploadForm] = useState({
        title: '',
        description: '',
        documentType: '',
        tags: ''
    });

    useEffect(() => {
        loadDocuments();
        loadDocumentTypes();
    }, []);

    const loadDocuments = async () => {
        try {
            setLoading(true);
            const data = await documentsAPI.getDocuments();
            setDocuments(data.documents || []);
        } catch (error) {
            console.error('Error loading documents:', error);
            alert('Error cargando documentos');
        } finally {
            setLoading(false);
        }
    };

    const loadDocumentTypes = async () => {
        try {
            const data = await documentsAPI.getDocumentTypes();
            setDocumentTypes(data.document_types || []);
        } catch (error) {
            console.error('Error loading document types:', error);
        }
    };

    const handleFileChange = (e) => {
        setSelectedFile(e.target.files[0]);
    };

    const handleInputChange = (e) => {
        setUploadForm({
            ...uploadForm,
            [e.target.name]: e.target.value
        });
    };

    const handleUpload = async (e) => {
        e.preventDefault();

        if (!selectedFile) {
            alert('Por favor selecciona un archivo');
            return;
        }

        if (!uploadForm.documentType) {
            alert('Por favor selecciona un tipo de documento');
            return;
        }

        try {
            setUploading(true);

            const tags = uploadForm.tags ? uploadForm.tags.split(',').map(tag => tag.trim()) : [];

            // Encontrar el tipo de documento seleccionado
            const selectedType = documentTypes.find(type => type.id === parseInt(uploadForm.documentType));
            if (!selectedType) {
                alert('Tipo de documento no válido');
                return;
            }

            await documentsAPI.uploadDocument(
                selectedFile,
                uploadForm.title || selectedFile.name,
                uploadForm.description,
                selectedType.type_name,  // Enviar el nombre del tipo, no el ID
                tags
            );

            alert('Documento subido exitosamente');

            // Limpiar formulario
            setSelectedFile(null);
            setUploadForm({
                title: '',
                description: '',
                documentType: '',
                tags: ''
            });
            document.getElementById('fileInput').value = '';

            // Recargar documentos
            loadDocuments();

        } catch (error) {
            console.error('Error uploading document:', error);
            alert('Error subiendo documento: ' + (error.response?.data?.detail || error.message));
        } finally {
            setUploading(false);
        }
    };

    const handleDownload = async (documentId) => {
        try {
            await documentsAPI.downloadDocument(documentId);
        } catch (error) {
            console.error('Error downloading document:', error);
            alert('Error descargando documento');
        }
    };

    const handleDelete = async (documentId) => {
        if (!confirm('¿Estás seguro de que quieres eliminar este documento?')) {
            return;
        }

        try {
            await documentsAPI.deleteDocument(documentId);
            alert('Documento eliminado exitosamente');
            loadDocuments();
        } catch (error) {
            console.error('Error deleting document:', error);
            alert('Error eliminando documento');
        }
    };

    return (
        <div className="p-6 max-w-6xl mx-auto">
            <h1 className="text-3xl font-bold mb-6">Gestión de Documentos</h1>

            {/* Formulario de subida */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                <h2 className="text-xl font-semibold mb-4">Subir Nuevo Documento</h2>

                <form onSubmit={handleUpload} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Archivo *
                        </label>
                        <input
                            id="fileInput"
                            type="file"
                            onChange={handleFileChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Título
                        </label>
                        <input
                            type="text"
                            name="title"
                            value={uploadForm.title}
                            onChange={handleInputChange}
                            placeholder="Título del documento (opcional)"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Tipo de Documento *
                        </label>
                        <select
                            name="documentType"
                            value={uploadForm.documentType}
                            onChange={handleInputChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        >
                            <option value="">Seleccionar tipo...</option>
                            {documentTypes.map(type => (
                                <option key={type.id} value={type.id}>
                                    {type.description} ({type.max_size_mb}MB máx.)
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Descripción
                        </label>
                        <textarea
                            name="description"
                            value={uploadForm.description}
                            onChange={handleInputChange}
                            placeholder="Descripción del documento (opcional)"
                            rows="3"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Tags
                        </label>
                        <input
                            type="text"
                            name="tags"
                            value={uploadForm.tags}
                            onChange={handleInputChange}
                            placeholder="Tags separados por comas (opcional)"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={uploading}
                        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    >
                        {uploading ? 'Subiendo...' : 'Subir Documento'}
                    </button>
                </form>
            </div>

            {/* Lista de documentos */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">Mis Documentos</h2>

                {loading ? (
                    <p className="text-center py-4">Cargando documentos...</p>
                ) : documents.length === 0 ? (
                    <p className="text-center py-4 text-gray-500">No tienes documentos subidos</p>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="min-w-full table-auto">
                            <thead>
                                <tr className="bg-gray-50">
                                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Archivo</th>
                                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Tipo</th>
                                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Tamaño</th>
                                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Fecha</th>
                                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {documents.map(doc => (
                                    <tr key={doc.id} className="border-t">
                                        <td className="px-4 py-2">
                                            <div>
                                                <div className="font-medium">{doc.original_filename}</div>
                                                {doc.description && (
                                                    <div className="text-sm text-gray-500">{doc.description}</div>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-4 py-2 text-sm">{doc.type_description}</td>
                                        <td className="px-4 py-2 text-sm">{doc.size_mb} MB</td>
                                        <td className="px-4 py-2 text-sm">
                                            {new Date(doc.created_at).toLocaleDateString()}
                                        </td>
                                        <td className="px-4 py-2">
                                            <div className="flex space-x-2">
                                                <button
                                                    onClick={() => handleDownload(doc.id)}
                                                    className="text-blue-600 hover:text-blue-800 text-sm"
                                                >
                                                    Descargar
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(doc.id)}
                                                    className="text-red-600 hover:text-red-800 text-sm"
                                                >
                                                    Eliminar
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default DocumentsComponent;