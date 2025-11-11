import React, { useEffect, useState } from 'react';
import { getDashboard, actualizarEstadoDocumental, anularReserva, enviarNotificacion } from '../../services/adminAPI';
import './AdminDashboard.css';

const AdminDashboard = () => {
    const [dashboard, setDashboard] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedReserva, setSelectedReserva] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [modalType, setModalType] = useState(''); // estado, anular, notificar

    useEffect(() => {
        cargarDashboard();
    }, []);

    const cargarDashboard = async () => {
        try {
            setLoading(true);
            const data = await getDashboard();
            setDashboard(data);
        } catch (error) {
            console.error('Error al cargar dashboard:', error);
            alert('Error al cargar dashboard');
        } finally {
            setLoading(false);
        }
    };

    const handleActualizarEstado = async (reservaId, nuevoEstado, notas) => {
        try {
            await actualizarEstadoDocumental(reservaId, nuevoEstado, notas);
            alert('✅ Estado actualizado exitosamente');
            cargarDashboard();
            setShowModal(false);
        } catch (error) {
            console.error('Error:', error);
            alert('❌ Error al actualizar estado');
        }
    };

    const handleAnular = async (reservaId, motivo) => {
        if (!motivo || motivo.trim() === '') {
            alert('Debe proporcionar un motivo de anulación');
            return;
        }

        try {
            await anularReserva(reservaId, motivo);
            alert('✅ Reserva anulada exitosamente');
            cargarDashboard();
            setShowModal(false);
        } catch (error) {
            console.error('Error:', error);
            alert('❌ Error al anular reserva');
        }
    };

    const handleNotificar = async (reservaId, tipo, mensaje) => {
        try {
            await enviarNotificacion(reservaId, tipo, mensaje);
            alert('✅ Notificación enviada');
            setShowModal(false);
        } catch (error) {
            console.error('Error:', error);
            alert('❌ Error al enviar notificación');
        }
    };

    const openModal = (reserva, type) => {
        setSelectedReserva(reserva);
        setModalType(type);
        setShowModal(true);
    };

    const getEstadoColor = (estado) => {
        const colores = {
            activa: '#10b981',
            completada: '#3b82f6',
            cancelada: '#ef4444',
            anulada: '#f59e0b'
        };
        return colores[estado] || '#6b7280';
    };

    const getEstadoDocColor = (estado) => {
        const colores = {
            completo: '#10b981',
            incompleto: '#f59e0b',
            pendiente: '#6b7280'
        };
        return colores[estado] || '#6b7280';
    };

    if (loading) {
        return (
            <div className="admin-dashboard">
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p>Cargando dashboard...</p>
                </div>
            </div>
        );
    }

    if (!dashboard) {
        return <div className="admin-dashboard"><p>No se pudieron cargar los datos</p></div>;
    }

    const { estadisticas, reservas, avance_digitalizacion } = dashboard;

    return (
        <div className="admin-dashboard">
            <div className="dashboard-header">
                <h1>📊 Dashboard Administrativo</h1>
                <button onClick={cargarDashboard} className="btn-refresh">
                    🔄 Actualizar
                </button>
            </div>

            {/* Estadísticas */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon">📋</div>
                    <div className="stat-content">
                        <h3>{estadisticas.total_reservas}</h3>
                        <p>Total Reservas</p>
                    </div>
                </div>

                <div className="stat-card active">
                    <div className="stat-icon">✅</div>
                    <div className="stat-content">
                        <h3>{estadisticas.reservas_activas}</h3>
                        <p>Activas</p>
                    </div>
                </div>

                <div className="stat-card completed">
                    <div className="stat-icon">🎉</div>
                    <div className="stat-content">
                        <h3>{estadisticas.reservas_completadas}</h3>
                        <p>Completadas</p>
                    </div>
                </div>

                <div className="stat-card canceled">
                    <div className="stat-icon">❌</div>
                    <div className="stat-content">
                        <h3>{estadisticas.reservas_anuladas}</h3>
                        <p>Anuladas</p>
                    </div>
                </div>

                <div className="stat-card doc-complete">
                    <div className="stat-icon">📄</div>
                    <div className="stat-content">
                        <h3>{estadisticas.docs_completos}</h3>
                        <p>Docs Completos</p>
                    </div>
                </div>

                <div className="stat-card doc-incomplete">
                    <div className="stat-icon">⚠️</div>
                    <div className="stat-content">
                        <h3>{estadisticas.docs_incompletos}</h3>
                        <p>Docs Incompletos</p>
                    </div>
                </div>

                <div className="stat-card doc-pending">
                    <div className="stat-icon">⏳</div>
                    <div className="stat-content">
                        <h3>{estadisticas.docs_pendientes}</h3>
                        <p>Docs Pendientes</p>
                    </div>
                </div>

                {avance_digitalizacion && (
                    <div className="stat-card digitalization">
                        <div className="stat-icon">💾</div>
                        <div className="stat-content">
                            <h3>{avance_digitalizacion.avance?.completados || 0}</h3>
                            <p>Docs Digitalizados</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Tabla de Reservas */}
            <div className="reservations-section">
                <h2>📋 Listado de Reservas</h2>
                <div className="table-container">
                    <table className="reservations-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Fecha</th>
                                <th>Hora</th>
                                <th>Usuario</th>
                                <th>RUT</th>
                                <th>Trámite</th>
                                <th>Estado</th>
                                <th>Estado Doc</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {reservas && reservas.length > 0 ? (
                                reservas.slice(0, 20).map((reserva) => (
                                    <tr key={reserva.id}>
                                        <td>{reserva.id}</td>
                                        <td>{new Date(reserva.fecha).toLocaleDateString()}</td>
                                        <td>{reserva.hora}</td>
                                        <td>{reserva.usuario_nombre}</td>
                                        <td>{reserva.usuario_rut || 'N/A'}</td>
                                        <td>
                                            <span className="tramite-badge">
                                                {reserva.tipo_tramite}
                                            </span>
                                        </td>
                                        <td>
                                            <span
                                                className="status-badge"
                                                style={{ background: getEstadoColor(reserva.estado) }}
                                            >
                                                {reserva.estado}
                                            </span>
                                        </td>
                                        <td>
                                            <span
                                                className="status-badge"
                                                style={{ background: getEstadoDocColor(reserva.estado_documental) }}
                                            >
                                                {reserva.estado_documental}
                                            </span>
                                        </td>
                                        <td>
                                            <div className="action-buttons">
                                                <button
                                                    onClick={() => openModal(reserva, 'estado')}
                                                    className="btn-action btn-estado"
                                                    title="Actualizar estado documental"
                                                >
                                                    📝
                                                </button>
                                                <button
                                                    onClick={() => openModal(reserva, 'notificar')}
                                                    className="btn-action btn-notificar"
                                                    title="Enviar notificación"
                                                >
                                                    📧
                                                </button>
                                                {reserva.estado === 'activa' && (
                                                    <button
                                                        onClick={() => openModal(reserva, 'anular')}
                                                        className="btn-action btn-anular"
                                                        title="Anular reserva"
                                                    >
                                                        ❌
                                                    </button>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="9" className="no-data">
                                        No hay reservas para mostrar
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Modal */}
            {showModal && selectedReserva && (
                <Modal
                    reserva={selectedReserva}
                    type={modalType}
                    onClose={() => setShowModal(false)}
                    onActualizarEstado={handleActualizarEstado}
                    onAnular={handleAnular}
                    onNotificar={handleNotificar}
                />
            )}
        </div>
    );
};

// Componente Modal
const Modal = ({ reserva, type, onClose, onActualizarEstado, onAnular, onNotificar }) => {
    const [estado, setEstado] = useState(reserva.estado_documental);
    const [notas, setNotas] = useState('');
    const [motivo, setMotivo] = useState('');
    const [tipoNotif, setTipoNotif] = useState('recordatorio');
    const [mensaje, setMensaje] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();

        if (type === 'estado') {
            onActualizarEstado(reserva.id, estado, notas);
        } else if (type === 'anular') {
            onAnular(reserva.id, motivo);
        } else if (type === 'notificar') {
            onNotificar(reserva.id, tipoNotif, mensaje);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>
                        {type === 'estado' && '📝 Actualizar Estado Documental'}
                        {type === 'anular' && '❌ Anular Reserva'}
                        {type === 'notificar' && '📧 Enviar Notificación'}
                    </h2>
                    <button onClick={onClose} className="btn-close">✕</button>
                </div>

                <div className="modal-body">
                    <div className="reserva-info">
                        <p><strong>Reserva:</strong> #{reserva.id}</p>
                        <p><strong>Usuario:</strong> {reserva.usuario_nombre}</p>
                        <p><strong>Fecha:</strong> {new Date(reserva.fecha).toLocaleDateString()} {reserva.hora}</p>
                    </div>

                    <form onSubmit={handleSubmit}>
                        {type === 'estado' && (
                            <>
                                <div className="form-group">
                                    <label>Estado Documental:</label>
                                    <select value={estado} onChange={(e) => setEstado(e.target.value)} required>
                                        <option value="pendiente">Pendiente</option>
                                        <option value="incompleto">Incompleto</option>
                                        <option value="completo">Completo</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label>Notas (opcional):</label>
                                    <textarea
                                        value={notas}
                                        onChange={(e) => setNotas(e.target.value)}
                                        placeholder="Agregar notas internas..."
                                        rows="3"
                                    />
                                </div>
                            </>
                        )}

                        {type === 'anular' && (
                            <div className="form-group">
                                <label>Motivo de Anulación: *</label>
                                <textarea
                                    value={motivo}
                                    onChange={(e) => setMotivo(e.target.value)}
                                    placeholder="Explique por qué se anula esta reserva..."
                                    rows="4"
                                    required
                                />
                            </div>
                        )}

                        {type === 'notificar' && (
                            <>
                                <div className="form-group">
                                    <label>Tipo de Notificación:</label>
                                    <select value={tipoNotif} onChange={(e) => setTipoNotif(e.target.value)}>
                                        <option value="recordatorio">Recordatorio</option>
                                        <option value="documentos_faltantes">Documentos Faltantes</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label>Mensaje:</label>
                                    <textarea
                                        value={mensaje}
                                        onChange={(e) => setMensaje(e.target.value)}
                                        placeholder="Escriba el mensaje a enviar..."
                                        rows="4"
                                        required
                                    />
                                </div>
                            </>
                        )}

                        <div className="modal-actions">
                            <button type="button" onClick={onClose} className="btn-cancel">
                                Cancelar
                            </button>
                            <button type="submit" className="btn-submit">
                                Confirmar
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
