import React, { useEffect, useState } from 'react';
import { getLicenciasPorVencer, enviarNotificacion } from '../../services/adminAPI';
import './VencimientosLicencias.css';

const VencimientosLicencias = () => {
    const [vencimientos, setVencimientos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [dias, setDias] = useState(30);
    const [filtro, setFiltro] = useState('todos'); // todos, critico, proximo

    useEffect(() => {
        cargarVencimientos();
    }, [dias]);

    const cargarVencimientos = async () => {
        try {
            setLoading(true);
            const data = await getLicenciasPorVencer(dias);
            setVencimientos(data.vencimientos || []);
        } catch (error) {
            console.error('Error al cargar vencimientos:', error);
            alert('Error al cargar vencimientos');
        } finally {
            setLoading(false);
        }
    };

    const handleNotificar = async (usuario) => {
        const mensaje = `Su licencia de conducir número ${usuario.licencia_numero} vence en ${usuario.dias_restantes} días (${usuario.fecha_vencimiento}). Por favor, acérquese a renovarla antes del vencimiento.`;

        try {
            // En este caso, necesitaríamos un endpoint específico para notificaciones de vencimiento
            // Por ahora, mostraremos un alert con la información
            if (confirm(`¿Enviar notificación de renovación a ${usuario.nombre}?\n\n${mensaje}`)) {
                alert('✅ Notificación enviada (simulado)');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('❌ Error al enviar notificación');
        }
    };

    const handleNotificarTodos = async () => {
        const vencimientosFiltrados = getVencimientosFiltrados();

        if (vencimientosFiltrados.length === 0) {
            alert('No hay vencimientos para notificar');
            return;
        }

        if (confirm(`¿Enviar notificaciones a ${vencimientosFiltrados.length} usuarios?`)) {
            alert(`✅ Se enviarían ${vencimientosFiltrados.length} notificaciones (simulado)`);
        }
    };

    const getSeveridad = (diasRestantes) => {
        if (diasRestantes <= 7) return 'critico';
        if (diasRestantes <= 15) return 'urgente';
        return 'proximo';
    };

    const getVencimientosFiltrados = () => {
        if (filtro === 'todos') return vencimientos;
        if (filtro === 'critico') return vencimientos.filter(v => v.dias_restantes <= 7);
        if (filtro === 'proximo') return vencimientos.filter(v => v.dias_restantes > 7);
        return vencimientos;
    };

    const vencimientosFiltrados = getVencimientosFiltrados();

    if (loading) {
        return (
            <div className="vencimientos-page">
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p>Cargando vencimientos...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="vencimientos-page">
            <div className="page-header">
                <h1>⏰ Vencimientos de Licencias</h1>
            </div>

            {/* Controles */}
            <div className="controls-card">
                <div className="control-group">
                    <label>Período de consulta:</label>
                    <select value={dias} onChange={(e) => setDias(Number(e.target.value))}>
                        <option value={7}>Próximos 7 días</option>
                        <option value={15}>Próximos 15 días</option>
                        <option value={30}>Próximos 30 días</option>
                        <option value={60}>Próximos 60 días</option>
                        <option value={90}>Próximos 90 días</option>
                    </select>
                </div>

                <div className="control-group">
                    <label>Filtrar por:</label>
                    <select value={filtro} onChange={(e) => setFiltro(e.target.value)}>
                        <option value="todos">Todos ({vencimientos.length})</option>
                        <option value="critico">Críticos ≤7 días ({vencimientos.filter(v => v.dias_restantes <= 7).length})</option>
                        <option value="proximo">Próximos &gt;7 días ({vencimientos.filter(v => v.dias_restantes > 7).length})</option>
                    </select>
                </div>

                <button onClick={handleNotificarTodos} className="btn-notify-all">
                    📧 Notificar a Todos
                </button>
            </div>

            {/* Estadísticas Rápidas */}
            <div className="stats-row">
                <div className="stat-box critico">
                    <h3>{vencimientos.filter(v => v.dias_restantes <= 7).length}</h3>
                    <p>Críticos (≤7 días)</p>
                </div>
                <div className="stat-box urgente">
                    <h3>{vencimientos.filter(v => v.dias_restantes > 7 && v.dias_restantes <= 15).length}</h3>
                    <p>Urgentes (8-15 días)</p>
                </div>
                <div className="stat-box proximo">
                    <h3>{vencimientos.filter(v => v.dias_restantes > 15).length}</h3>
                    <p>Próximos (&gt;15 días)</p>
                </div>
            </div>

            {/* Lista de Vencimientos */}
            <div className="vencimientos-card">
                <h2>📋 Licencias por Vencer</h2>

                {vencimientosFiltrados.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">✅</div>
                        <h3>No hay licencias por vencer</h3>
                        <p>En el período seleccionado no hay licencias próximas a vencer</p>
                    </div>
                ) : (
                    <div className="vencimientos-list">
                        {vencimientosFiltrados.map((vencimiento, index) => (
                            <div
                                key={index}
                                className={`vencimiento-item severidad-${getSeveridad(vencimiento.dias_restantes)}`}
                            >
                                <div className="vencimiento-header">
                                    <div className="user-info">
                                        <h3>{vencimiento.nombre}</h3>
                                        <span className="user-rut">{vencimiento.rut}</span>
                                    </div>
                                    <div className={`dias-badge ${getSeveridad(vencimiento.dias_restantes)}`}>
                                        {vencimiento.dias_restantes} {vencimiento.dias_restantes === 1 ? 'día' : 'días'}
                                    </div>
                                </div>

                                <div className="vencimiento-details">
                                    <div className="detail-row">
                                        <span className="detail-label">📧 Email:</span>
                                        <span>{vencimiento.email}</span>
                                    </div>
                                    <div className="detail-row">
                                        <span className="detail-label">📞 Teléfono:</span>
                                        <span>{vencimiento.telefono || 'No registrado'}</span>
                                    </div>
                                    <div className="detail-row">
                                        <span className="detail-label">🪪 Licencia:</span>
                                        <span>{vencimiento.licencia_numero}</span>
                                    </div>
                                    <div className="detail-row">
                                        <span className="detail-label">📅 Vence:</span>
                                        <span className="fecha-vencimiento">
                                            {new Date(vencimiento.fecha_vencimiento).toLocaleDateString()}
                                        </span>
                                    </div>
                                    {vencimiento.categorias && (
                                        <div className="detail-row">
                                            <span className="detail-label">🚗 Categorías:</span>
                                            <span>{vencimiento.categorias}</span>
                                        </div>
                                    )}
                                </div>

                                <div className="vencimiento-actions">
                                    <button
                                        onClick={() => handleNotificar(vencimiento)}
                                        className="btn-notify"
                                    >
                                        📧 Enviar Recordatorio
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default VencimientosLicencias;
