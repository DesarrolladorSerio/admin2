import React from 'react';
import './Footer.css';

const Footer = () => {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="app-footer">
            <div className="footer-container">
                <div className="footer-section">
                    <h3>🏛️ Sistema Municipal</h3>
                    <p>Plataforma de gestión de trámites y reservaciones</p>
                </div>

                <div className="footer-section">
                    <h4>Enlaces</h4>
                    <ul>
                        <li><a href="/reservas">Reservar Hora</a></li>
                        <li><a href="/admin">Panel Admin</a></li>
                        <li><a href="/digitalizador">Digitalización</a></li>
                    </ul>
                </div>

                <div className="footer-section">
                    <h4>Contacto</h4>
                    <p>📧 contacto@municipio.cl</p>
                    <p>📞 +56 2 1234 5678</p>
                </div>

                <div className="footer-section">
                    <h4>Horario de Atención</h4>
                    <p>Lunes a Viernes</p>
                    <p>08:00 - 17:00 hrs</p>
                </div>
            </div>

            <div className="footer-bottom">
                <p>&copy; {currentYear} Municipalidad. Todos los derechos reservados.</p>
            </div>
        </footer>
    );
};

export default Footer;
