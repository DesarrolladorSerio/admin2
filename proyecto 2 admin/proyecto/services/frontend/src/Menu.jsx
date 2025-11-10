import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authAPI from "./services/authAPI";

export default function Menu() {
    const navigate = useNavigate();
    const [currentUser, setCurrentUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadUserData = async () => {
            if (!authAPI.isAuthenticated()) {
                navigate('/login');
                return;
            }

            try {
                const userData = await authAPI.getCurrentUser();
                setCurrentUser(userData);
            } catch (error) {
                console.error('Error loading user data:', error);
                authAPI.logout(); // Si hay error, cerrar sesión
                navigate('/login');
            } finally {
                setLoading(false);
            }
        };

        loadUserData();
    }, [navigate]);

    const handleLogout = () => {
        authAPI.logout();
        navigate('/login');
    };

    if (!authAPI.isAuthenticated() || loading) {
        return (
            <div style={{ padding: '20px', textAlign: 'center' }}>
                {loading ? '🔄 Cargando...' : null}
            </div>
        );
    }

    const displayName = currentUser?.nombre || currentUser?.username || 'Usuario';

    return (
        <div style={{ padding: '20px', maxWidth: '600px', margin: '50px auto', textAlign: 'center' }}>
            <h1>👋 Bienvenido, {displayName}</h1>
            <div style={{
                marginBottom: '30px',
                padding: '15px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px',
                border: '1px solid #e9ecef'
            }}>
                <p><strong>📧 Email:</strong> {currentUser?.email}</p>
                {currentUser?.rut && <p><strong>🆔 RUT:</strong> {currentUser.rut}</p>}
            </div>
            {/* Principio de Responsabilidad Única: Separamos las opciones por tipo de usuario */}
            <MenuOptions
                userRole={currentUser?.role}
                onNavigate={navigate}
                onLogout={handleLogout}
            />
        </div>
    );
}

// Principio de Responsabilidad Única: Componente especializado en mostrar opciones de menú
function MenuOptions({ userRole, onNavigate, onLogout }) {
    // Principio de Composición: Crear un botón reutilizable
    const MenuButton = ({ onClick, background, children, isAdmin = false }) => {
        // Principio de Principio Abierto/Cerrado: Solo mostrar botones de admin si el usuario es admin
        if (isAdmin && userRole !== 'admin') {
            return null;
        }

        return (
            <button
                onClick={onClick}
                style={{
                    padding: '12px 20px',
                    background,
                    color: '#fff',
                    border: 'none',
                    borderRadius: 6,
                    marginRight: '10px',
                    marginBottom: '10px',
                    fontSize: '16px',
                    cursor: 'pointer',
                    display: 'inline-block'
                }}
            >
                {children}
            </button>
        );
    };

    return (
        <div style={{ marginTop: '20px' }}>
            {/* Opciones disponibles para todos los usuarios */}
            <MenuButton
                onClick={() => onNavigate('/reservas')}
                background="#007bff"
            >
                📅 Ir a Reservas
            </MenuButton>

            {/* Gestión avanzada de reservas para admin/empleados */}
            {(userRole === 'admin' || userRole === 'employee') && (
                <MenuButton
                    onClick={() => onNavigate('/admin/reservas')}
                    background="#17a2b8"
                >
                    🔧 Gestionar Todas las Reservas
                </MenuButton>
            )}

            <MenuButton
                onClick={() => onNavigate('/documentos')}
                background="#28a745"
            >
                📄 Documentos
            </MenuButton>

            {/* Principio de Segregación de Interfaces: Opciones específicas para administradores */}
            <MenuButton
                onClick={() => onNavigate('/admin/register-employee')}
                background="#6f42c1"
                isAdmin={true}
            >
                👥 Registrar Empleado
            </MenuButton>

            <MenuButton
                onClick={() => onNavigate('/admin/reports')}
                background="#fd7e14"
                isAdmin={true}
            >
                📊 Reportes
            </MenuButton>

            <MenuButton
                onClick={() => onNavigate('/admin/users')}
                background="#20c997"
                isAdmin={true}
            >
                👤 Gestionar Usuarios
            </MenuButton>

            {/* Opción de cerrar sesión (disponible para todos) */}
            <MenuButton
                onClick={onLogout}
                background="#dc3545"
            >
                🚪 Cerrar Sesión
            </MenuButton>

            {/* Indicador visual del rol del usuario */}
            {userRole === 'admin' && (
                <div style={{
                    marginTop: '20px',
                    padding: '10px',
                    background: '#e7f3ff',
                    border: '1px solid #b3d7ff',
                    borderRadius: '4px',
                    fontSize: '14px'
                }}>
                    🔐 <strong>Panel de Administración Activo</strong>
                </div>
            )}

            {/* Información sobre el asistente IA */}
            <div style={{
                marginTop: '20px',
                padding: '10px',
                background: '#f3e5ff',
                border: '1px solid #d1b3ff',
                borderRadius: '4px',
                fontSize: '14px'
            }}>
                🤖 <strong>Asistente IA disponible</strong><br />
                Busca el botón flotante en la esquina inferior derecha
            </div>
        </div>
    );
}