import React from 'react';

export default function Calendar({
  reservations,
  currentUser,
  selectedDate,
  onDateSelect,
  onEditReservation,
  onDeleteReservation
}) {

  // Obtener reservaciones del día seleccionado
  const selectedDateStr = selectedDate.toISOString().split('T')[0];
  const dayReservations = reservations.filter(r => String(r.fecha) === selectedDateStr);

  // Generar días del mes actual
  const generateCalendarDays = () => {
    const year = selectedDate.getFullYear();
    const month = selectedDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();

    const days = [];
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      const dateStr = date.toISOString().split('T')[0];
      const hasReservations = reservations.some(r => r.fecha === dateStr);

      days.push({
        day,
        date,
        dateStr,
        hasReservations,
        isSelected: dateStr === selectedDateStr
      });
    }
    return days;
  };

  const calendarDays = generateCalendarDays();
  const monthNames = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];

  return (
    <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
      {/* 📅 Calendario */}
      <div style={{ flex: '1', minWidth: '300px' }}>
        <h3 style={{ textAlign: 'center' }}>
          📅 {monthNames[selectedDate.getMonth()]} {selectedDate.getFullYear()}
        </h3>

        {/* Navegación de meses */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
          <button
            onClick={() => {
              const newDate = new Date(selectedDate);
              newDate.setMonth(newDate.getMonth() - 1);
              onDateSelect(newDate);
            }}
            style={{ padding: '5px 10px', cursor: 'pointer' }}
          >
            ← Anterior
          </button>

          <button
            onClick={() => onDateSelect(new Date())}
            style={{ padding: '5px 10px', cursor: 'pointer' }}
          >
            Hoy
          </button>

          <button
            onClick={() => {
              const newDate = new Date(selectedDate);
              newDate.setMonth(newDate.getMonth() + 1);
              onDateSelect(newDate);
            }}
            style={{ padding: '5px 10px', cursor: 'pointer' }}
          >
            Siguiente →
          </button>
        </div>

        {/* Días de la semana */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(7, 1fr)',
          gap: '2px',
          marginBottom: '5px'
        }}>
          {['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do'].map(day => (
            <div key={day} style={{
              padding: '5px',
              textAlign: 'center',
              fontWeight: 'bold',
              backgroundColor: '#f8f9fa'
            }}>
              {day}
            </div>
          ))}
        </div>

        {/* Días del mes */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(7, 1fr)',
          gap: '2px'
        }}>
          {calendarDays.map(({ day, date, hasReservations, isSelected }) => (
            <button
              key={day}
              onClick={() => onDateSelect(date)}
              style={{
                padding: '15px 5px',
                border: '1px solid #ddd',
                backgroundColor: isSelected ? '#007bff' : hasReservations ? '#e7f3ff' : 'white',
                color: isSelected ? 'white' : '#333',
                cursor: 'pointer',
                position: 'relative'
              }}
            >
              {day}
              {hasReservations && (
                <span style={{
                  position: 'absolute',
                  bottom: '2px',
                  right: '2px',
                  fontSize: '8px'
                }}>
                  🔴
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* 📋 Reservaciones del día */}
      <div style={{ flex: '1', minWidth: '300px' }}>
        <h3>📅 Reservaciones del {selectedDateStr}</h3>

        {dayReservations.length === 0 ? (
          <div style={{
            padding: '20px',
            textAlign: 'center',
            backgroundColor: '#f8f9fa',
            borderRadius: '5px',
            color: '#666'
          }}>
            📝 No hay reservaciones para este día
          </div>
        ) : (
          dayReservations.map(reservation => (
            <div key={reservation.id} style={{
              border: '1px solid #ddd',
              borderRadius: '5px',
              padding: '15px',
              marginBottom: '10px',
              backgroundColor: 'white'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                    🕐 {reservation.hora?.slice(0, 5)} - {
                      reservation.usuario_id === currentUser?.id
                        ? (currentUser?.nombre || currentUser?.username || 'Usuario actual')
                        : (reservation.usuario_nombre || 'Usuario desconocido')
                    }
                  </div>
                  <div style={{ color: '#0066cc', marginBottom: '5px', fontWeight: 'bold' }}>
                    🏛️ {reservation.tipo_tramite || 'Trámite no especificado'}
                  </div>
                  <div style={{ color: '#666', marginBottom: '5px' }}>
                    📝 {reservation.descripcion}
                  </div>
                  <div style={{ fontSize: '12px', color: '#999' }}>
                    🏷️ Estado: {reservation.estado}
                  </div>
                </div>

                {currentUser && currentUser.id === reservation.usuario_id && (
                  <div style={{ display: 'flex', gap: '5px' }}>
                    <button
                      onClick={() => onEditReservation(reservation)}
                      style={{
                        padding: '5px 10px',
                        backgroundColor: '#ffc107',
                        color: 'white',
                        border: 'none',
                        borderRadius: '3px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      ✏️ Editar
                    </button>

                    <button
                      onClick={() => onDeleteReservation(reservation.id)}
                      style={{
                        padding: '5px 10px',
                        backgroundColor: '#dc3545',
                        color: 'white',
                        border: 'none',
                        borderRadius: '3px',
                        cursor: 'pointer',
                        fontSize: '12px'
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
    </div>
  );
}
