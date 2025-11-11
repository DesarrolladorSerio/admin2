import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import authAPI from '../services/authAPI';

// Principio de Responsabilidad Única: Este componente se encarga únicamente de proteger rutas
export default function AdminRoute({ children, allowEmployee = false }) {
    const [isAuthorized, setIsAuthorized] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkAuthorization = async () => {
            // Verificar si está autenticado
            if (!authAPI.isAuthenticated()) {
                setIsAuthorized(false);
                setLoading(false);
                return;
            }

            try {
                // Obtener datos del usuario actual
                const userData = await authAPI.getCurrentUser();

                // Verificar permisos según configuración
                const allowedRoles = allowEmployee ? ['admin', 'employee'] : ['admin'];
                if (userData && allowedRoles.includes(userData.role)) {
                    setIsAuthorized(true);
                } else {
                    setIsAuthorized(false);
                }
            } catch (error) {
                console.error('Error checking authorization:', error);
                setIsAuthorized(false);
            } finally {
                setLoading(false);
            }
        };

        checkAuthorization();
    }, []);

    // Mostrar loading mientras verificamos permisos
    if (loading) {
        return (
            <div style={{
                padding: '50px',
                textAlign: 'center',
                fontSize: '18px'
            }}>
                🔍 Verificando permisos...
            </div>
        );
    }

    // Si no está autorizado, redirigir al menú principal
    if (!isAuthorized) {
        return <Navigate to="/menu" replace />;
    }

    // Si está autorizado, mostrar el componente hijo
    return children;
}