import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Header.css';

const Header = () => {
    const navigate = useNavigate();
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const isLoggedIn = !!localStorage.getItem('token');

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/login');
    };

    return (
        <header className="app-header">
            <div className="header-container">
                <div className="header-logo">
                    <Link to="/">
                        <h1>🏛️ Sistema Municipal</h1>
                    </Link>
                </div>

                <nav className="header-nav">
                    {isLoggedIn ? (
                        <>
                            <Link to="/reservas" className="nav-link">
                                📅 Reservas
                            </Link>

                            {(user.role === 'admin' || user.role === 'employee') && (
                                <Link to="/admin" className="nav-link">
                                    👨‍💼 Administración
                                </Link>
                            )}

                            {(user.role === 'admin' || user.role === 'digitalizador') && (
                                <Link to="/digitalizador" className="nav-link">
                                    📄 Digitalización
                                </Link>
                            )}

                            <div className="user-menu">
                                <span className="user-name">
                                    👤 {user.nombre || user.username}
                                </span>
                                <span className="user-role">
                                    ({user.role})
                                </span>
                                <button onClick={handleLogout} className="logout-btn">
                                    🚪 Salir
                                </button>
                            </div>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="nav-link">
                                🔐 Iniciar Sesión
                            </Link>
                            <Link to="/register" className="nav-link">
                                📝 Registrarse
                            </Link>
                        </>
                    )}
                </nav>
            </div>
        </header>
    );
};

export default Header;
