import React, { useState } from 'react';

export default function ReservationList({
  reservations,
  currentUser,
  onEditReservation,
  onDeleteReservation
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDate, setFilterDate] = useState('');

  // Filtrar reservaciones
  const filteredReservations = reservations.filter(reservation => {
    const matchesSearch = searchTerm === '' ||
      (reservation.usuario_nombre || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (reservation.descripcion || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (reservation.tipo_tramite || '').toLowerCase().includes(searchTerm.toLowerCase());

    const matchesDate = filterDate === '' || String(reservation.fecha) === filterDate;

    return matchesSearch && matchesDate;
  });

  // Ordenar por fecha y hora (más recientes primero)
  const sortedReservations = [...filteredReservations].sort((a, b) => {
    const dateA = new Date(a.fecha + ' ' + a.hora);
    const dateB = new Date(b.fecha + ' ' + b.hora);
    return dateB - dateA;
  });

  return (
    <div>
      <h2>📋 Todas las Reservaciones</h2>

      {/* Barra de búsqueda y filtros */}
      <div style={{
        display: 'flex',
        gap: '10px',
        marginBottom: '20px',
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        <div style={{ flex: '1', minWidth: '200px' }}>
          <input
            type="text"
            placeholder="🔍 Buscar por usuario, trámite o descripción..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px'
            }}
          />
        </div>

        <div>
          <input
            type="date"
            value={filterDate}
            onChange={(e) => setFilterDate(e.target.value)}
            style={{
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px'
            }}
          />
        </div>

        {(searchTerm || filterDate) && (
          <button
            onClick={() => {
              setSearchTerm('');
              setFilterDate('');
            }}
            style={{
              padding: '10px 15px',
              backgroundColor: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            🔄 Limpiar Filtros
          </button>
        )}
      </div>

      {/* Contador de resultados */}
      <div style={{
        marginBottom: '15px',
        color: '#666',
        fontSize: '14px'
      }}>
        {sortedReservations.length} reservación(es) encontrada(s)
      </div>

      {/* Lista de reservaciones */}
      {sortedReservations.length === 0 ? (
        <div style={{
          padding: '40px',
          textAlign: 'center',
          backgroundColor: '#f8f9fa',
          borderRadius: '5px',
          color: '#666'
        }}>
          {searchTerm || filterDate ?
            '🔍 No se encontraron reservaciones con los filtros aplicados' :
            '📝 No hay reservaciones registradas'
          }
        </div>
      ) : (
        sortedReservations.map(reservation => (
          <div
            key={reservation.id}
            style={{
              border: '1px solid #ddd',
              borderRadius: '8px',
              padding: '20px',
              marginBottom: '15px',
              backgroundColor: 'white',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
          >
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              flexWrap: 'wrap',
              gap: '10px'
            }}>
              <div style={{ flex: 1, minWidth: '250px' }}>
                <div style={{
                  fontSize: '18px',
                  fontWeight: 'bold',
                  marginBottom: '10px',
                  color: '#333'
                }}>
                  📅 {reservation.fecha} 🕐 {reservation.hora.slice(0, 5)}
                </div>

                <div style={{ marginBottom: '8px', color: '#555' }}>
                  👤 <strong>Usuario:</strong> {
                    reservation.usuario_id === currentUser?.id
                      ? (currentUser?.nombre || currentUser?.username || 'Usuario actual')
                      : (reservation.usuario_nombre || 'Usuario desconocido')
                  }
                </div>

                <div style={{ marginBottom: '8px', color: '#555' }}>
                  🏛️ <strong>Tipo de Trámite:</strong> {reservation.tipo_tramite || 'No especificado'}
                </div>

                <div style={{ marginBottom: '8px', color: '#555' }}>
                  📝 <strong>Descripción:</strong> {reservation.descripcion || 'Sin descripción'}
                </div>

                <div style={{
                  display: 'inline-block',
                  padding: '4px 12px',
                  borderRadius: '12px',
                  fontSize: '12px',
                  fontWeight: 'bold',
                  backgroundColor: reservation.estado === 'activa' ? '#d4edda' :
                    reservation.estado === 'cancelada' ? '#f8d7da' : '#d1ecf1',
                  color: reservation.estado === 'activa' ? '#155724' :
                    reservation.estado === 'cancelada' ? '#721c24' : '#0c5460'
                }}>
                  🏷️ {reservation.estado.toUpperCase()}
                </div>
              </div>

              {/* Mostrar botones si es el propietario O si es admin/employee */}
              {currentUser && (
                currentUser.id === reservation.usuario_id ||
                currentUser.role === 'admin' ||
                currentUser.role === 'employee'
              ) && (
                  <div style={{
                    display: 'flex',
                    gap: '8px',
                    flexWrap: 'wrap'
                  }}>
                    <button
                      onClick={() => onEditReservation(reservation)}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: '#ffc107',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: 'bold'
                      }}
                    >
                      ✏️ Editar
                    </button>

                    <button
                      onClick={() => onDeleteReservation(reservation.id)}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: '#dc3545',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: 'bold'
                      }}
                    >
                      🗑️ Eliminar
                    </button>
                  </div>
                )}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
