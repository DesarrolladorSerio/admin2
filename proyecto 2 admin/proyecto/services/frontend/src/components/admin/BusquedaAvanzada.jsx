import React, { useState } from 'react';
import { buscarReservas, getEstadisticasTramites, exportarCSV } from '../../services/adminAPI';
import './BusquedaAvanzada.css';

const BusquedaAvanzada = () => {
    const [filtros, setFiltros] = useState({
        nombre: '',
        rut: '',
        tipo_tramite: '',
        categoria_tramite: '',
        fecha_inicio: '',
        fecha_fin: '',
        estado: '',
        estado_documental: ''
    });

    const [resultados, setResultados] = useState(null);
    const [estadisticas, setEstadisticas] = useState(null);
    const [loading, setLoading] = useState(false);
    const [tabActivo, setTabActivo] = useState('busqueda'); // busqueda, estadisticas

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFiltros(prev => ({ ...prev, [name]: value }));
    };

    const handleBuscar = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            // Filtrar campos vacíos
            const filtrosLimpios = Object.fromEntries(
                Object.entries(filtros).filter(([_, value]) => value !== '')
            );

            const data = await buscarReservas(filtrosLimpios);
            setResultados(data);
        } catch (error) {
            console.error('Error en búsqueda:', error);
            alert('Error al realizar la búsqueda');
        } finally {
            setLoading(false);
        }
    };

    const handleEstadisticas = async () => {
        setLoading(true);

        try {
            const fechaInicio = filtros.fecha_inicio || null;
            const fechaFin = filtros.fecha_fin || null;

            const data = await getEstadisticasTramites(fechaInicio, fechaFin);
            setEstadisticas(data);
            setTabActivo('estadisticas');
        } catch (error) {
            console.error('Error al obtener estadísticas:', error);
            alert('Error al obtener estadísticas');
        } finally {
            setLoading(false);
        }
    };

    const handleExportar = () => {
        if (!resultados || !resultados.resultados) {
            alert('No hay datos para exportar');
            return;
        }

        const datosExportar = resultados.resultados.map(r => ({
            ID: r.id,
            Fecha: new Date(r.fecha).toLocaleDateString(),
            Hora: r.hora,
            Usuario: r.usuario_nombre,
            RUT: r.usuario_rut || 'N/A',
            'Tipo Trámite': r.tipo_tramite,
            Categoría: r.categoria_tramite || 'N/A',
            Estado: r.estado,
            'Estado Documental': r.estado_documental
        }));

        exportarCSV(datosExportar, `busqueda_reservas_${new Date().toISOString().split('T')[0]}`);
    };

    const limpiarFiltros = () => {
        setFiltros({
            nombre: '',
            rut: '',
            tipo_tramite: '',
            categoria_tramite: '',
            fecha_inicio: '',
            fecha_fin: '',
            estado: '',
            estado_documental: ''
        });
        setResultados(null);
        setEstadisticas(null);
    };

    return (
        <div className="busqueda-avanzada">
            <div className="page-header">
                <h1>🔍 Búsqueda Avanzada de Reservas</h1>
            </div>

            {/* Formulario de Búsqueda */}
            <div className="search-card">
                <form onSubmit={handleBuscar}>
                    <div className="filters-grid">
                        <div className="form-group">
                            <label>Nombre del Usuario</label>
                            <input
                                type="text"
                                name="nombre"
                                value={filtros.nombre}
                                onChange={handleInputChange}
                                placeholder="Buscar por nombre..."
                            />
                        </div>

                        <div className="form-group">
                            <label>RUT</label>
                            <input
                                type="text"
                                name="rut"
                                value={filtros.rut}
                                onChange={handleInputChange}
                                placeholder="12345678-9"
                            />
                        </div>

                        <div className="form-group">
                            <label>Categoría de Trámite</label>
                            <select name="categoria_tramite" value={filtros.categoria_tramite} onChange={handleInputChange}>
                                <option value="">Todas las categorías</option>
                                <option value="primer_otorgamiento">Primer Otorgamiento</option>
                                <option value="primer_otorgamiento_profesional">Primer Otorg. Profesional</option>
                                <option value="renovacion">Renovación</option>
                                <option value="duplicado">Duplicado</option>
                                <option value="canje">Canje</option>
                                <option value="especial">Especial</option>
                                <option value="modificacion">Modificación</option>
                                <option value="otros">Otros</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label>Estado</label>
                            <select name="estado" value={filtros.estado} onChange={handleInputChange}>
                                <option value="">Todos los estados</option>
                                <option value="activa">Activa</option>
                                <option value="completada">Completada</option>
                                <option value="cancelada">Cancelada</option>
                                <option value="anulada">Anulada</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label>Estado Documental</label>
                            <select name="estado_documental" value={filtros.estado_documental} onChange={handleInputChange}>
                                <option value="">Todos</option>
                                <option value="pendiente">Pendiente</option>
                                <option value="incompleto">Incompleto</option>
                                <option value="completo">Completo</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label>Fecha Inicio</label>
                            <input
                                type="date"
                                name="fecha_inicio"
                                value={filtros.fecha_inicio}
                                onChange={handleInputChange}
                            />
                        </div>

                        <div className="form-group">
                            <label>Fecha Fin</label>
                            <input
                                type="date"
                                name="fecha_fin"
                                value={filtros.fecha_fin}
                                onChange={handleInputChange}
                            />
                        </div>
                    </div>

                    <div className="form-actions">
                        <button type="button" onClick={limpiarFiltros} className="btn-secondary">
                            🔄 Limpiar
                        </button>
                        <button type="button" onClick={handleEstadisticas} className="btn-stats">
                            📊 Ver Estadísticas
                        </button>
                        <button type="submit" className="btn-primary" disabled={loading}>
                            {loading ? 'Buscando...' : '🔍 Buscar'}
                        </button>
                    </div>
                </form>
            </div>

            {/* Tabs */}
            {(resultados || estadisticas) && (
                <div className="tabs">
                    <button
                        className={`tab ${tabActivo === 'busqueda' ? 'active' : ''}`}
                        onClick={() => setTabActivo('busqueda')}
                    >
                        📋 Resultados ({resultados?.count || 0})
                    </button>
                    {estadisticas && (
                        <button
                            className={`tab ${tabActivo === 'estadisticas' ? 'active' : ''}`}
                            onClick={() => setTabActivo('estadisticas')}
                        >
                            📊 Estadísticas
                        </button>
                    )}
                </div>
            )}

            {/* Resultados de Búsqueda */}
            {tabActivo === 'busqueda' && resultados && (
                <div className="results-card">
                    <div className="results-header">
                        <h2>📋 Resultados de la Búsqueda</h2>
                        <div className="results-actions">
                            <span className="result-count">
                                {resultados.count} {resultados.count === 1 ? 'resultado' : 'resultados'}
                            </span>
                            <button onClick={handleExportar} className="btn-export">
                                📥 Exportar a CSV
                            </button>
                        </div>
                    </div>

                    <div className="table-container">
                        <table className="results-table">
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
                                </tr>
                            </thead>
                            <tbody>
                                {resultados.resultados.map((reserva) => (
                                    <tr key={reserva.id}>
                                        <td>{reserva.id}</td>
                                        <td>{new Date(reserva.fecha).toLocaleDateString()}</td>
                                        <td>{reserva.hora}</td>
                                        <td>{reserva.usuario_nombre}</td>
                                        <td>{reserva.usuario_rut || 'N/A'}</td>
                                        <td>{reserva.tipo_tramite}</td>
                                        <td>
                                            <span className={`badge badge-${reserva.estado}`}>
                                                {reserva.estado}
                                            </span>
                                        </td>
                                        <td>
                                            <span className={`badge badge-doc-${reserva.estado_documental}`}>
                                                {reserva.estado_documental}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Estadísticas */}
            {tabActivo === 'estadisticas' && estadisticas && (
                <div className="stats-card">
                    <h2>📊 Estadísticas de Trámites</h2>

                    <div className="stats-summary">
                        <div className="summary-card">
                            <h3>{estadisticas.total_tramites}</h3>
                            <p>Total de Trámites</p>
                        </div>
                    </div>

                    <div className="stats-sections">
                        {/* Ranking por Trámite */}
                        <div className="stat-section">
                            <h3>🏆 Top Trámites</h3>
                            <div className="ranking-list">
                                {estadisticas.ranking_tramites.slice(0, 10).map((item, index) => (
                                    <div key={index} className="ranking-item">
                                        <span className="ranking-number">#{index + 1}</span>
                                        <span className="ranking-name">{item.tipo_tramite}</span>
                                        <span className="ranking-count">{item.cantidad}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Ranking por Categoría */}
                        <div className="stat-section">
                            <h3>📁 Por Categoría</h3>
                            <div className="ranking-list">
                                {estadisticas.ranking_categorias.map((item, index) => (
                                    <div key={index} className="ranking-item">
                                        <span className="ranking-number">#{index + 1}</span>
                                        <span className="ranking-name">{item.categoria}</span>
                                        <span className="ranking-count">{item.cantidad}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default BusquedaAvanzada;
