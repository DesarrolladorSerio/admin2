import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Menu() {
    const navigate = useNavigate();
    const username = localStorage.getItem('username') || '';

    if (!username) {
        // si no hay usuario, redirigir a login
        navigate('/login');
        return null;
    }

    return (
        <div style={{ padding: '20px', maxWidth: '600px', margin: '50px auto', textAlign: 'center' }}>
            <h1>Bienvenido a menu, {username}</h1>
            <p style={{ marginTop: '20px' }}>
                <button onClick={() => navigate('/reservas')} style={{ padding: '10px 16px', background: '#007bff', color: '#fff', border: 'none', borderRadius: 4 }}>
                    Ir a Reservas
                </button>
            </p>
        </div>
    );
}