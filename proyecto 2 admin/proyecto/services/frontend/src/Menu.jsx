import React, { useEffect, useState } from 'react';
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
            <p style={{ marginTop: '20px' }}>
                <button
                    onClick={() => navigate('/reservas')}
                    style={{
                        padding: '12px 20px',
                        background: '#007bff',
                        color: '#fff',
                        border: 'none',
                        borderRadius: 6,
                        marginRight: '10px',
                        fontSize: '16px',
                        cursor: 'pointer'
                    }}
                >
                    📅 Ir a Reservas
                </button>
                <button
                    onClick={handleLogout}
                    style={{
                        padding: '12px 20px',
                        background: '#dc3545',
                        color: '#fff',
                        border: 'none',
                        borderRadius: 6,
                        fontSize: '16px',
                        cursor: 'pointer'
                    }}
                >
                    🚪 Cerrar Sesión
                </button>
            </p>
        </div>
    );
}