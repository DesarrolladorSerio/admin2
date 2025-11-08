import { useEffect, useState } from 'react';
import authAPI from '../services/authAPI';
import reservationAPI from '../services/reservationAPI';

export default function AdminReservations() {
    const [reservations, setReservations] = useState([]);
    const [currentUser, setCurrentUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedReservation, setSelectedReservation] = useState(null);

    useEffect(() => {
        loadInitialData();
    }, []);

    const loadInitialData = async () => {
        setLoading(true);
        try {
            const [user, reservationsData] = await Promise.all([
                authAPI.getCurrentUser(),
                reservationAPI.getAllReservationsDetailed() // Nuevo método para admin
            ]);

            // Verificar que el usuario tenga permisos
            if (!['admin', 'employee'].includes(user.role)) {
                alert('❌ No tienes permisos para acceder a esta sección');
                return;
            }

            setCurrentUser(user);
            setReservations(reservationsData);
        } catch (error) {
            console.error('Error loading data:', error);
            alert('Error al cargar datos de reservas');
        }
        setLoading(false);
    };

    const handleDeleteReservation = async (reservationId, userInfo) => {
        const confirmMessage = `¿Estás seguro de eliminar la reserva de ${userInfo.usuario_nombre}?\n\nFecha: ${userInfo.fecha}\nHora: ${userInfo.hora}\nServicio: ${userInfo.tipo_tramite}`;

        if (!window.confirm(confirmMessage)) {
            return;
        }

        try {
            await reservationAPI.deleteReservation(reservationId);
            setReservations(reservations.filter(r => r.id !== reservationId));
            alert('✅ Reserva eliminada exitosamente');
        } catch (error) {
            console.error('Error deleting reservation:', error);
            alert('❌ Error al eliminar la reserva');
        }
    };

    const getStatusBadge = (estado) => {
        const colors = {
            'activa': '#28a745',
            'cancelada': '#dc3545',
            'completada': '#007bff'
        };

        return (
            <span style={{
                backgroundColor: colors[estado] || '#6c757d',
                color: 'white',
                padding: '4px 8px',
                borderRadius: '12px',
                fontSize: '12px',
                fontWeight: 'bold'
            }}>
                {estado.toUpperCase()}
            </span>
        );
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-CL');
    };

    if (loading) {
        return (
            <div style={{ padding: '20px', textAlign: 'center' }}>
                🔄 Cargando reservas...
            </div>
        );
    }

    return (
        <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
            <div style={{
                marginBottom: '20px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <h1>🔧 Gestión de Reservas - {currentUser?.role === 'admin' ? 'Administrador' : 'Empleado'}</h1>
                <button
                    onClick={() => window.history.back()}
                    style={{
                        padding: '8px 16px',
                        backgroundColor: '#6c757d',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    ← Volver
                </button>
            </div>

            <div style={{ marginBottom: '20px' }}>
                <p>📊 Total de reservas: <strong>{reservations.length}</strong></p>
                <p>✅ Activas: <strong>{reservations.filter(r => r.estado === 'activa').length}</strong></p>
            </div>

            {/* Tabla de reservas */}
            <div style={{ overflowX: 'auto' }}>
                <table style={{
                    width: '100%',
                    borderCollapse: 'collapse',
                    backgroundColor: 'white',
                    borderRadius: '8px',
                    overflow: 'hidden',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}>
                    <thead style={{ backgroundColor: '#f8f9fa' }}>
                        <tr>
                            <th style={tableHeaderStyle}>ID</th>
                            <th style={tableHeaderStyle}>Usuario</th>
                            <th style={tableHeaderStyle}>Email</th>
                            <th style={tableHeaderStyle}>Fecha</th>
                            <th style={tableHeaderStyle}>Hora</th>
                            <th style={tableHeaderStyle}>Servicio</th>
                            <th style={tableHeaderStyle}>Estado</th>
                            <th style={tableHeaderStyle}>Creada</th>
                            <th style={tableHeaderStyle}>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {reservations.map((reservation) => (
                            <tr key={reservation.id} style={{ borderBottom: '1px solid #e9ecef' }}>
                                <td style={tableCellStyle}>{reservation.id}</td>
                                <td style={tableCellStyle}>
                                    <strong>{reservation.usuario_nombre}</strong>
                                    <br />
                                    <small style={{ color: '#6c757d' }}>ID: {reservation.usuario_id}</small>
                                </td>
                                <td style={tableCellStyle}>
                                    {reservation.usuario_email || 'No disponible'}
                                </td>
                                <td style={tableCellStyle}>{formatDate(reservation.fecha)}</td>
                                <td style={tableCellStyle}>{reservation.hora}</td>
                                <td style={tableCellStyle}>
                                    <small style={{
                                        backgroundColor: '#e9ecef',
                                        padding: '2px 6px',
                                        borderRadius: '4px'
                                    }}>
                                        {reservation.tipo_tramite}
                                    </small>
                                </td>
                                <td style={tableCellStyle}>{getStatusBadge(reservation.estado)}</td>
                                <td style={tableCellStyle}>
                                    {formatDate(reservation.created_at)}
                                </td>
                                <td style={tableCellStyle}>
                                    <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                                        <button
                                            onClick={() => setSelectedReservation(reservation)}
                                            style={{
                                                padding: '4px 8px',
                                                backgroundColor: '#007bff',
                                                color: 'white',
                                                border: 'none',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                                fontSize: '12px'
                                            }}
                                        >
                                            👁️ Ver
                                        </button>

                                        {reservation.estado === 'activa' && (
                                            <button
                                                onClick={() => handleDeleteReservation(reservation.id, reservation)}
                                                style={{
                                                    padding: '4px 8px',
                                                    backgroundColor: '#dc3545',
                                                    color: 'white',
                                                    border: 'none',
                                                    borderRadius: '4px',
                                                    cursor: 'pointer',
                                                    fontSize: '12px'
                                                }}
                                            >
                                                🗑️ Eliminar
                                            </button>
                                        )}
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {reservations.length === 0 && (
                <div style={{
                    textAlign: 'center',
                    padding: '40px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '8px',
                    margin: '20px 0'
                }}>
                    📅 No hay reservas registradas
                </div>
            )}

            {/* Modal de detalles */}
            {selectedReservation && (
                <ReservationDetailsModal
                    reservation={selectedReservation}
                    onClose={() => setSelectedReservation(null)}
                />
            )}
        </div>
    );
}

// Modal para mostrar detalles de una reserva
function ReservationDetailsModal({ reservation, onClose }) {
    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
        }}>
            <div style={{
                backgroundColor: 'white',
                padding: '20px',
                borderRadius: '8px',
                maxWidth: '500px',
                width: '90%',
                maxHeight: '80vh',
                overflow: 'auto'
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h3>📋 Detalles de Reserva #{reservation.id}</h3>
                    <button
                        onClick={onClose}
                        style={{
                            backgroundColor: '#dc3545',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            padding: '5px 10px',
                            cursor: 'pointer'
                        }}
                    >
                        ✕
                    </button>
                </div>

                <div style={{ lineHeight: '1.6' }}>
                    <p><strong>👤 Usuario:</strong> {reservation.usuario_nombre}</p>
                    <p><strong>🆔 ID Usuario:</strong> {reservation.usuario_id}</p>
                    <p><strong>📧 Email:</strong> {reservation.usuario_email || 'No disponible'}</p>
                    <p><strong>📅 Fecha:</strong> {new Date(reservation.fecha).toLocaleDateString('es-CL')}</p>
                    <p><strong>🕒 Hora:</strong> {reservation.hora}</p>
                    <p><strong>📋 Servicio:</strong> {reservation.tipo_tramite}</p>
                    <p><strong>📝 Descripción:</strong> {reservation.descripcion || 'Sin descripción'}</p>
                    <p><strong>📊 Estado:</strong> {reservation.estado}</p>
                    <p><strong>📆 Creada:</strong> {new Date(reservation.created_at).toLocaleString('es-CL')}</p>
                </div>
            </div>
        </div>
    );
}

// Estilos para las tablas
const tableHeaderStyle = {
    padding: '12px',
    textAlign: 'left',
    fontWeight: 'bold',
    borderBottom: '2px solid #dee2e6'
};

const tableCellStyle = {
    padding: '12px',
    verticalAlign: 'top'
};