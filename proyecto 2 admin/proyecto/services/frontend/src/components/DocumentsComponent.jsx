import React, { useState, useEffect } from 'react';
import authAPI from '../services/authAPI';
import digitalizadorAPI from '../services/digitalizadorAPI';

const DocumentsComponent = () => {
    const [documents, setDocuments] = useState([]);
    const [currentUser, setCurrentUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [tipoDocumento, setTipoDocumento] = useState('');
    const [reservaId, setReservaId] = useState('');


    useEffect(() => {
        const loadInitialData = async () => {
            try {
                setLoading(true);
                const user = await authAPI.getCurrentUser();
                setCurrentUser(user);
                if (user && user.id) {
                    const userDocs = await digitalizadorAPI.getDocumentosUsuario(user.id);
                    setDocuments(userDocs.documentos || []);
                }
            } catch (error) {
                console.error('Error loading initial data:', error);
                alert('Error cargando sus datos. Por favor, intente recargar la página.');
            } finally {
                setLoading(false);
            }
        };

        loadInitialData();
    }, []);

    const handleFileChange = (e) => {
        setSelectedFile(e.target.files[0]);
    };

    const handleUpload = async (e) => {
        e.preventDefault();

        if (!selectedFile) {
            alert('Por favor selecciona un archivo');
            return;
        }
        if (!tipoDocumento) {
            alert('Por favor especifica un tipo de documento');
            return;
        }

        try {
            setUploading(true);
            await digitalizadorAPI.subirDocumentoCiudadano(
                selectedFile,
                reservaId || null, // Enviar null si está vacío
                tipoDocumento
            );

            alert('Documento subido exitosamente');

            // Limpiar formulario y recargar
            setSelectedFile(null);
            setTipoDocumento('');
            setReservaId('');
            document.getElementById('fileInput').value = '';
            
            if (currentUser && currentUser.id) {
                const userDocs = await digitalizadorAPI.getDocumentosUsuario(currentUser.id);
                setDocuments(userDocs.documentos || []);
            }

        } catch (error) {
            console.error('Error uploading document:', error);
            alert('Error subiendo documento: ' + (error.response?.data?.detail || error.message));
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="p-6 max-w-6xl mx-auto bg-gray-50 min-h-screen">
            <h1 className="text-3xl font-bold mb-6 text-gray-800">Mi Repositorio de Documentos</h1>

            {/* Formulario de subida */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                <h2 className="text-xl font-semibold mb-4 text-gray-700">Subir Nuevo Documento</h2>

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
                            Tipo de Documento *
                        </label>
                        <input
                            type="text"
                            value={tipoDocumento}
                            onChange={(e) => setTipoDocumento(e.target.value)}
                            placeholder="Ej: Cédula, Certificado de Antecedentes"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        />
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            ID de Reserva (Opcional)
                        </label>
                        <input
                            type="number"
                            value={reservaId}
                            onChange={(e) => setReservaId(e.target.value)}
                            placeholder="Si el documento es para una reserva específica"
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
                <h2 className="text-xl font-semibold mb-4 text-gray-700">Mis Documentos Subidos</h2>

                {loading ? (
                    <p className="text-center py-4">Cargando documentos...</p>
                ) : documents.length === 0 ? (
                    <p className="text-center py-4 text-gray-500">No tienes documentos subidos.</p>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="min-w-full table-auto">
                            <thead className="bg-gray-100">
                                <tr >
                                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600 uppercase">Nombre Archivo</th>
                                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600 uppercase">Tipo</th>
                                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600 uppercase">ID Reserva</th>
                                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600 uppercase">Fecha de Subida</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {documents.map(doc => (
                                    <tr key={doc.id}>
                                        <td className="px-4 py-3 whitespace-nowrap">{doc.nombre_archivo}</td>
                                        <td className="px-4 py-3 whitespace-nowrap">{doc.tipo_documento}</td>
                                        <td className="px-4 py-3 whitespace-nowrap">{doc.reserva_id || 'N/A'}</td>
                                        <td className="px-4 py-3 whitespace-nowrap">
                                            {new Date(doc.created_at).toLocaleDateString()}
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