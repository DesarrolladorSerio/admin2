import React, { useState, useEffect } from 'react';
import authAPI from '../services/authAPI';

export default function DatosMunicipales() {
    const [loading, setLoading] = useState(true);
    const [datos, setDatos] = useState(null);
    const [error, setError] = useState(null);
    const [consultaProgress, setConsultaProgress] = useState(0);
    const [consultaStatus, setConsultaStatus] = useState('Iniciando consulta...');

    useEffect(() => {
        consultarDatos();
    }, []);

    const consultarDatos = async () => {
        setLoading(true);
        setError(null);
        setConsultaProgress(0);

        try {
            // Simular pasos de consulta con mensajes
            const pasos = [
                { progreso: 10, mensaje: '🔍 Conectando con bases de datos municipales...' },
                { progreso: 25, mensaje: '🚗 Consultando Licencias de Conducir...' },
                { progreso: 40, mensaje: '🏗️ Revisando Permisos de Edificación...' },
                { progreso: 55, mensaje: '🏪 Verificando Patentes Comerciales...' },
                { progreso: 70, mensaje: '⚖️ Consultando Juzgado de Policía Local...' },
                { progreso: 85, mensaje: '🗑️ Verificando Servicio de Aseo...' },
                { progreso: 100, mensaje: '✅ Consulta completada!' }
            ];

            for (const paso of pasos) {
                setConsultaProgress(paso.progreso);
                setConsultaStatus(paso.mensaje);
                await new Promise(resolve => setTimeout(resolve, 300));
            }

            const response = await authAPI.consultarDatosMunicipales();
            setDatos(response);
            setLoading(false);

        } catch (err) {
            console.error('Error al consultar datos municipales:', err);
            setError(err.response?.data?.detail || 'Error al consultar datos municipales');
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div style={{
                padding: '40px',
                maxWidth: '800px',
                margin: '0 auto',
                textAlign: 'center'
            }}>
                <h1 style={{ fontSize: '28px', marginBottom: '30px', color: '#2c3e50' }}>
                    🏛️ Consulta de Datos Municipales
                </h1>

                <div style={{
                    backgroundColor: 'white',
                    borderRadius: '12px',
                    padding: '40px',
                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                }}>
                    <div style={{
                        width: '80px',
                        height: '80px',
                        border: '8px solid #e0e0e0',
                        borderTop: '8px solid #3498db',
                        borderRadius: '50%',
                        margin: '0 auto 30px',
                        animation: 'spin 1s linear infinite'
                    }} />

                    <h2 style={{ fontSize: '22px', marginBottom: '15px', color: '#34495e' }}>
                        {consultaStatus}
                    </h2>

                    <div style={{
                        width: '100%',
                        height: '30px',
                        backgroundColor: '#ecf0f1',
                        borderRadius: '15px',
                        overflow: 'hidden',
                        margin: '20px 0'
                    }}>
                        <div style={{
                            width: `${consultaProgress}%`,
                            height: '100%',
                            backgroundColor: '#3498db',
                            transition: 'width 0.3s ease',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                            fontWeight: 'bold',
                            fontSize: '14px'
                        }}>
                            {consultaProgress}%
                        </div>
                    </div>

                    <p style={{ color: '#7f8c8d', fontSize: '14px', marginTop: '15px' }}>
                        ⏳ Por favor espere mientras consultamos las bases de datos...
                    </p>
                </div>

                <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
                <div style={{
                    backgroundColor: '#fee',
                    border: '2px solid #fcc',
                    borderRadius: '8px',
                    padding: '20px',
                    textAlign: 'center'
                }}>
                    <h2 style={{ color: '#c00' }}>❌ Error en la Consulta</h2>
                    <p>{error}</p>
                    <button
                        onClick={consultarDatos}
                        style={{
                            marginTop: '20px',
                            padding: '10px 20px',
                            backgroundColor: '#3498db',
                            color: 'white',
                            border: 'none',
                            borderRadius: '5px',
                            cursor: 'pointer'
                        }}
                    >
                        🔄 Reintentar
                    </button>
                </div>
            </div>
        );
    }

    if (!datos || !datos.datos_municipales) {
        return <div>No hay datos disponibles</div>;
    }

    const { usuario, datos_municipales } = datos;
    const { licencia_conducir, permisos_edificacion, patentes_comerciales, multas_jpl, servicio_aseo } = datos_municipales;

    return (
        <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
            {/* Header */}
            <div style={{
                backgroundColor: '#3498db',
                color: 'white',
                padding: '30px',
                borderRadius: '12px',
                marginBottom: '30px',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
            }}>
                <h1 style={{ margin: '0 0 10px 0', fontSize: '32px' }}>
                    🏛️ Panel de Datos Municipales
                </h1>
                <p style={{ margin: 0, fontSize: '18px', opacity: 0.9 }}>
                    {usuario.nombre} | RUT: {usuario.rut}
                </p>
                <p style={{ margin: '5px 0 0 0', fontSize: '14px', opacity: 0.8 }}>
                    📅 Consultado el {datos_municipales.fecha_consulta}
                </p>
            </div>

            {/* Licencia de Conducir */}
            <SectionCard
                titulo="🚗 Licencia de Conducir"
                icono="🚗"
                color="#27ae60"
            >
                {licencia_conducir.tiene_licencia ? (
                    <div>
                        <InfoRow label="N° Licencia" value={licencia_conducir.numero_licencia} />
                        <InfoRow label="Clase" value={licencia_conducir.clase} bold />
                        <InfoRow label="Tipo" value={licencia_conducir.tipo} />
                        <InfoRow
                            label="Estado"
                            value={licencia_conducir.estado}
                            badge
                            badgeColor={licencia_conducir.vigente ? '#27ae60' : '#e74c3c'}
                        />
                        <InfoRow label="Fecha Otorgamiento" value={licencia_conducir.fecha_otorgamiento} />
                        <InfoRow label="Fecha Vencimiento" value={licencia_conducir.fecha_vencimiento} />
                        <InfoRow label="Restricciones" value={licencia_conducir.restricciones} />
                        <InfoRow label="Puntos Acumulados" value={licencia_conducir.puntos} />

                        {licencia_conducir.multas_pendientes > 0 && (
                            <div style={{
                                backgroundColor: '#fee',
                                border: '2px solid #fcc',
                                borderRadius: '8px',
                                padding: '15px',
                                marginTop: '15px'
                            }}>
                                <p style={{ margin: 0, fontWeight: 'bold', color: '#c00' }}>
                                    ⚠️ Multas Pendientes: {licencia_conducir.multas_pendientes}
                                </p>
                                <p style={{ margin: '5px 0 0 0', color: '#c00' }}>
                                    Monto: ${licencia_conducir.monto_multas.toLocaleString()}
                                </p>
                            </div>
                        )}
                    </div>
                ) : (
                    <p style={{ textAlign: 'center', color: '#7f8c8d', fontStyle: 'italic' }}>
                        {licencia_conducir.mensaje}
                    </p>
                )}
            </SectionCard>

            {/* Permisos de Edificación */}
            <SectionCard
                titulo="🏗️ Permisos de Edificación"
                icono="🏗️"
                color="#e67e22"
            >
                {permisos_edificacion.length > 0 ? (
                    permisos_edificacion.map((permiso, idx) => (
                        <div
                            key={idx}
                            style={{
                                backgroundColor: '#f8f9fa',
                                border: '1px solid #dee2e6',
                                borderRadius: '8px',
                                padding: '15px',
                                marginBottom: '15px'
                            }}
                        >
                            <h4 style={{ margin: '0 0 10px 0', color: '#2c3e50' }}>
                                {permiso.tipo}
                            </h4>
                            <InfoRow label="N° Permiso" value={permiso.numero_permiso} />
                            <InfoRow label="Dirección" value={permiso.direccion} />
                            <InfoRow label="Fecha Solicitud" value={permiso.fecha_solicitud} />
                            <InfoRow
                                label="Estado"
                                value={permiso.estado}
                                badge
                                badgeColor={
                                    permiso.estado === 'Aprobado' ? '#27ae60' :
                                        permiso.estado === 'Finalizado' ? '#95a5a6' :
                                            permiso.estado === 'Rechazado' ? '#e74c3c' : '#f39c12'
                                }
                            />
                            <InfoRow label="Monto Pagado" value={`$${permiso.monto_pagado.toLocaleString()}`} />
                            <InfoRow label="Inspector" value={permiso.inspector_asignado} />
                        </div>
                    ))
                ) : (
                    <p style={{ textAlign: 'center', color: '#7f8c8d', fontStyle: 'italic' }}>
                        No se encontraron permisos de edificación registrados
                    </p>
                )}
            </SectionCard>

            {/* Patentes Comerciales */}
            <SectionCard
                titulo="🏪 Patentes Comerciales"
                icono="🏪"
                color="#9b59b6"
            >
                {patentes_comerciales.length > 0 ? (
                    patentes_comerciales.map((patente, idx) => (
                        <div
                            key={idx}
                            style={{
                                backgroundColor: '#f8f9fa',
                                border: '1px solid #dee2e6',
                                borderRadius: '8px',
                                padding: '15px',
                                marginBottom: '15px'
                            }}
                        >
                            <h4 style={{ margin: '0 0 10px 0', color: '#2c3e50' }}>
                                {patente.nombre_comercial}
                            </h4>
                            <InfoRow label="N° Patente" value={patente.numero_patente} />
                            <InfoRow label="Giro" value={patente.giro} bold />
                            <InfoRow label="Dirección" value={patente.direccion} />
                            <InfoRow
                                label="Estado"
                                value={patente.estado}
                                badge
                                badgeColor={patente.vigente ? '#27ae60' : '#e74c3c'}
                            />
                            <InfoRow label="Fecha Vencimiento" value={patente.fecha_vencimiento} />
                            <InfoRow label="Monto Anual" value={`$${patente.monto_anual.toLocaleString()}`} />

                            {patente.deuda_acumulada > 0 && (
                                <div style={{
                                    backgroundColor: '#fee',
                                    border: '2px solid #fcc',
                                    borderRadius: '8px',
                                    padding: '10px',
                                    marginTop: '10px'
                                }}>
                                    <p style={{ margin: 0, fontWeight: 'bold', color: '#c00' }}>
                                        ⚠️ Deuda Acumulada: ${patente.deuda_acumulada.toLocaleString()}
                                    </p>
                                </div>
                            )}
                        </div>
                    ))
                ) : (
                    <p style={{ textAlign: 'center', color: '#7f8c8d', fontStyle: 'italic' }}>
                        No se encontraron patentes comerciales registradas
                    </p>
                )}
            </SectionCard>

            {/* Multas JPL */}
            <SectionCard
                titulo="⚖️ Juzgado de Policía Local (JPL)"
                icono="⚖️"
                color="#e74c3c"
            >
                {multas_jpl.length > 0 ? (
                    multas_jpl.map((multa, idx) => (
                        <div
                            key={idx}
                            style={{
                                backgroundColor: multa.pagada ? '#d4edda' : '#fff3cd',
                                border: `2px solid ${multa.pagada ? '#c3e6cb' : '#ffc107'}`,
                                borderRadius: '8px',
                                padding: '15px',
                                marginBottom: '15px'
                            }}
                        >
                            <h4 style={{ margin: '0 0 10px 0', color: '#2c3e50' }}>
                                {multa.infraccion}
                            </h4>
                            <InfoRow label="N° Causa" value={multa.numero_causa} />
                            <InfoRow label="Fecha Infracción" value={multa.fecha_infraccion} />
                            <InfoRow label="Monto" value={`$${multa.monto.toLocaleString()}`} bold />
                            <InfoRow
                                label="Estado"
                                value={multa.estado}
                                badge
                                badgeColor={multa.pagada ? '#27ae60' : '#f39c12'}
                            />
                            {!multa.pagada && (
                                <InfoRow label="Vence" value={multa.fecha_vencimiento} />
                            )}
                        </div>
                    ))
                ) : (
                    <p style={{ textAlign: 'center', color: '#27ae60', fontWeight: 'bold' }}>
                        ✅ No hay multas registradas
                    </p>
                )}
            </SectionCard>

            {/* Servicio de Aseo */}
            <SectionCard
                titulo="🗑️ Servicio de Aseo Municipal"
                icono="🗑️"
                color="#16a085"
            >
                {servicio_aseo.tiene_servicio ? (
                    <div>
                        <InfoRow label="N° Cliente" value={servicio_aseo.numero_cliente} />
                        <InfoRow label="Propiedades Registradas" value={servicio_aseo.propiedades_registradas} />
                        <InfoRow label="Tipo Servicio" value={servicio_aseo.tipo_servicio} />
                        <InfoRow label="Frecuencia Recolección" value={servicio_aseo.frecuencia_recoleccion} />
                        <InfoRow
                            label="Estado de Pago"
                            value={servicio_aseo.estado}
                            badge
                            badgeColor={servicio_aseo.al_dia ? '#27ae60' : '#e74c3c'}
                        />

                        {servicio_aseo.direcciones.map((dir, idx) => (
                            <InfoRow key={idx} label={`Dirección ${idx + 1}`} value={dir} />
                        ))}

                        {!servicio_aseo.al_dia && (
                            <div style={{
                                backgroundColor: '#fee',
                                border: '2px solid #fcc',
                                borderRadius: '8px',
                                padding: '15px',
                                marginTop: '15px'
                            }}>
                                <p style={{ margin: 0, fontWeight: 'bold', color: '#c00' }}>
                                    ⚠️ Deuda Pendiente
                                </p>
                                <p style={{ margin: '5px 0 0 0', color: '#c00' }}>
                                    Meses en mora: {servicio_aseo.meses_deuda}
                                </p>
                                <p style={{ margin: '5px 0 0 0', color: '#c00' }}>
                                    Monto: ${servicio_aseo.monto_deuda.toLocaleString()}
                                </p>
                            </div>
                        )}
                    </div>
                ) : (
                    <p style={{ textAlign: 'center', color: '#7f8c8d', fontStyle: 'italic' }}>
                        {servicio_aseo.mensaje}
                    </p>
                )}
            </SectionCard>

            {/* Botón de refrescar */}
            <div style={{ textAlign: 'center', marginTop: '30px' }}>
                <button
                    onClick={consultarDatos}
                    style={{
                        padding: '15px 30px',
                        backgroundColor: '#3498db',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        fontSize: '16px',
                        fontWeight: 'bold',
                        cursor: 'pointer',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                    }}
                >
                    🔄 Actualizar Datos
                </button>
            </div>
        </div>
    );
}

// Componente para tarjetas de sección
function SectionCard({ titulo, icono, color, children }) {
    return (
        <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '25px',
            marginBottom: '25px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            border: `3px solid ${color}`
        }}>
            <h2 style={{
                margin: '0 0 20px 0',
                fontSize: '24px',
                color: color,
                borderBottom: `2px solid ${color}`,
                paddingBottom: '10px'
            }}>
                {icono} {titulo}
            </h2>
            {children}
        </div>
    );
}

// Componente para filas de información
function InfoRow({ label, value, bold, badge, badgeColor }) {
    return (
        <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            padding: '10px 0',
            borderBottom: '1px solid #ecf0f1'
        }}>
            <span style={{ color: '#7f8c8d', fontWeight: '500' }}>{label}:</span>
            {badge ? (
                <span style={{
                    backgroundColor: badgeColor,
                    color: 'white',
                    padding: '4px 12px',
                    borderRadius: '12px',
                    fontSize: '14px',
                    fontWeight: 'bold'
                }}>
                    {value}
                </span>
            ) : (
                <span style={{ fontWeight: bold ? 'bold' : 'normal', color: '#2c3e50' }}>
                    {value}
                </span>
            )}
        </div>
    );
}
