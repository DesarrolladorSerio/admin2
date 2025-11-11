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

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen bg-gray-100">
                <div className="text-xl font-semibold text-gray-700">🔄 Cargando...</div>
            </div>
        );
    }

    const displayName = currentUser?.nombre || currentUser?.username || 'Usuario';

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center p-4">
            <div className="w-full max-w-2xl bg-white shadow-lg rounded-lg p-8 mt-10">
                <h1 className="text-3xl font-bold text-center text-gray-800 mb-4">👋 ¡Bienvenido, {displayName}!</h1>
                <div className="mb-8 p-4 bg-gray-50 rounded-lg border border-gray-200 text-gray-700">
                    <p><strong className="font-semibold">📧 Email:</strong> {currentUser?.email}</p>
                    {currentUser?.rut && <p><strong className="font-semibold">🆔 RUT:</strong> {currentUser.rut}</p>}
                </div>
                <MenuOptions
                    userRole={currentUser?.role}
                    onNavigate={navigate}
                    onLogout={handleLogout}
                />
            </div>
        </div>
    );
}

function MenuOptions({ userRole, onNavigate, onLogout }) {
    const MenuButton = ({ onClick, className, children, isAdmin = false }) => {
        if (isAdmin && userRole !== 'admin') {
            return null;
        }

        return (
            <button
                onClick={onClick}
                className={`w-full text-left px-4 py-3 mb-3 text-white font-semibold rounded-lg shadow-md transition-transform transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-opacity-50 ${className}`}
            >
                {children}
            </button>
        );
    };

    return (
        <div className="mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Opciones de Usuario */}
                <MenuButton
                    onClick={() => onNavigate('/reservas')}
                    className="bg-blue-500 hover:bg-blue-600 focus:ring-blue-400"
                >
                    📅 Mis Reservas
                </MenuButton>
                <MenuButton
                    onClick={() => onNavigate('/documentos')}
                    className="bg-green-500 hover:bg-green-600 focus:ring-green-400"
                >
                    📄 Mis Documentos
                </MenuButton>
                <MenuButton
                    onClick={() => onNavigate('/datos-municipales')}
                    className="bg-indigo-500 hover:bg-indigo-600 focus:ring-indigo-400"
                >
                    🏛️ Mis Datos Municipales
                </MenuButton>

                {/* Opciones de Admin/Empleado */}
                {(userRole === 'admin' || userRole === 'employee') && (
                    <MenuButton
                        onClick={() => onNavigate('/admin/reservas')}
                        className="bg-teal-500 hover:bg-teal-600 focus:ring-teal-400"
                    >
                        🔧 Gestionar Todas las Reservas
                    </MenuButton>
                )}

                {/* Opciones solo para Admin */}
                <MenuButton
                    onClick={() => onNavigate('/admin/reports')}
                    className="bg-orange-500 hover:bg-orange-600 focus:ring-orange-400"
                    isAdmin={true}
                >
                    📊 Reportes y Estadísticas
                </MenuButton>
                <MenuButton
                    onClick={() => onNavigate('/admin/users')}
                    className="bg-purple-500 hover:bg-purple-600 focus:ring-purple-400"
                    isAdmin={true}
                >
                    👤 Gestionar Usuarios
                </MenuButton>
                {/* El botón "Registrar Empleado" se ha ocultado según la solicitud del usuario */}
                {/* <MenuButton
                    onClick={() => onNavigate('/admin/register-employee')}
                    className="bg-gray-600 hover:bg-gray-700 focus:ring-gray-500"
                    isAdmin={true}
                >
                    👥 Registrar Empleado
                </MenuButton> */}
            </div>

            {/* Logout y Avisos */}
            <div className="mt-8 border-t pt-6">
                <MenuButton
                    onClick={onLogout}
                    className="bg-red-500 hover:bg-red-600 focus:ring-red-400"
                >
                    🚪 Cerrar Sesión
                </MenuButton>

                {userRole === 'admin' && (
                    <div className="mt-4 p-3 bg-blue-100 border border-blue-300 text-blue-800 rounded-lg text-sm text-center">
                        🔐 <strong>Panel de Administración Activo</strong>
                    </div>
                )}
                <div className="mt-4 p-3 bg-purple-100 border border-purple-300 text-purple-800 rounded-lg text-sm text-center">
                    🤖 <strong>Asistente IA disponible</strong> en la esquina inferior derecha.
                </div>
            </div>
        </div>
    );
}