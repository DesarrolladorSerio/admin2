import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authAPI from "./services/authAPI";

export default function Menu() {
    const navigate = useNavigate();
    const [username, setUsername] = useState('');

    useEffect(() => {
        if (!authAPI.isAuthenticated()) {
            navigate('/login');
        } else {
            // Aquí podrías decodificar el token para obtener el username o hacer una llamada a /users/me
            // Por ahora, usaremos un placeholder o podrías implementar la lógica para obtener el username
            setUsername("Usuario Autenticado"); // Placeholder
        }
    }, [navigate]);

    const handleLogout = () => {
        authAPI.logout();
        navigate('/login');
    };

    if (!authAPI.isAuthenticated()) {
        return null;
    }

    return (
        <div style={{ padding: '20px', maxWidth: '600px', margin: '50px auto', textAlign: 'center' }}>
            <h1>Bienvenido al menú, {username}</h1>
            <p style={{ marginTop: '20px' }}>
                <button onClick={() => navigate('/reservas')} style={{ padding: '10px 16px', background: '#007bff', color: '#fff', border: 'none', borderRadius: 4, marginRight: '10px' }}>
                    Ir a Reservas
                </button>
                <button onClick={handleLogout} style={{ padding: '10px 16px', background: '#dc3545', color: '#fff', border: 'none', borderRadius: 4 }}>
                    Cerrar Sesión
                </button>
            </p>
        </div>
    );
}