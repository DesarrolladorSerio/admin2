import React, { useState, useEffect } from 'react';
import reservationAPI from '../services/reservationAPI';

export default function ReservationForm({
  currentUser,
  editingReservation,
  onSubmit,
  onCancel
}) {
  const [formData, setFormData] = useState({
    fecha: '',
    hora: '',
    tipo_tramite: '',
    descripcion: ''
  });

  const [tiposTramites, setTiposTramites] = useState([]);
  const [availabilityStatus, setAvailabilityStatus] = useState(null);
  const [checkingAvailability, setCheckingAvailability] = useState(false);

  useEffect(() => {
    // Cargar tipos de trámites
    const loadTiposTramites = async () => {
      try {
        const tipos = await reservationAPI.getTiposTramites();
        setTiposTramites(tipos);
      } catch (error) {
        console.error('Error cargando tipos de trámites:', error);
      }
    };

    loadTiposTramites();

    if (editingReservation) {
      // Si estamos editando, llenamos el formulario con los datos existentes
      setFormData({
        fecha: editingReservation.fecha,
        hora: editingReservation.hora.slice(0, 5), // Formato HH:MM
        tipo_tramite: editingReservation.tipo_tramite || '',
        descripcion: editingReservation.descripcion
      });
    } else {
      // Si es una nueva reserva, usamos valores por defecto
      const today = new Date().toISOString().split('T')[0];
      const now = new Date().toTimeString().slice(0, 5);
      setFormData({
        fecha: today,
        hora: now,
        tipo_tramite: '',
        descripcion: ''
      });
    }
  }, [editingReservation]);

  // Función para verificar disponibilidad
  const checkAvailability = async (fecha, hora, tipoTramite) => {
    if (!fecha || !hora || !tipoTramite) {
      setAvailabilityStatus(null);
      return;
    }

    setCheckingAvailability(true);
    try {
      const reservationId = editingReservation ? editingReservation.id : null;
      const result = await reservationAPI.checkAvailability(fecha, hora, tipoTramite, reservationId);
      setAvailabilityStatus(result);
    } catch (error) {
      console.error('Error checking availability:', error);
      setAvailabilityStatus({ available: false, message: 'Error al verificar disponibilidad' });
    } finally {
      setCheckingAvailability(false);
    }
  };

  // Verificar disponibilidad cuando cambien los datos relevantes
  useEffect(() => {
    const delayTimer = setTimeout(() => {
      checkAvailability(formData.fecha, formData.hora, formData.tipo_tramite);
    }, 500); // Delay para evitar muchas consultas mientras el usuario escribe

    return () => clearTimeout(delayTimer);
  }, [formData.fecha, formData.hora, formData.tipo_tramite]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.fecha || !formData.hora || !formData.tipo_tramite) {
      alert('❌ Por favor completa la fecha, hora y tipo de trámite');
      return;
    }

    // Verificar disponibilidad antes de enviar
    if (availabilityStatus && !availabilityStatus.available) {
      alert(`❌ ${availabilityStatus.message}`);
      return;
    }

    // Añadir siempre los datos del usuario actual al enviar
    const submitData = {
      ...formData,
      hora: formData.hora + ':00', // Agregar segundos
      usuario_id: currentUser.id,
      usuario_nombre: currentUser.nombre || currentUser.username // Usar nombre completo si está disponible
    };

    onSubmit(submitData);
  };

  return (
    <div style={{ maxWidth: '500px', margin: '0 auto' }}>
      <h2>
        {editingReservation ? '✏️ Editar Reservación' : '➕ Nueva Reservación'}
      </h2>

      <form onSubmit={handleSubmit} style={{
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '20px',
        backgroundColor: 'white'
      }}>

        {/* 👤 Muestra del Usuario Autenticado */}
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            👤 Usuario:
          </label>
          <p style={{
            width: '100%',
            padding: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '14px',
            backgroundColor: '#e9ecef'
          }}>
            {currentUser ? currentUser.username : 'Cargando...'}
          </p>
        </div>

        {/* 📅 Fecha */}
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            📅 Fecha: *
          </label>
          <input
            type="date"
            value={formData.fecha}
            onChange={(e) => setFormData({ ...formData, fecha: e.target.value })}
            required
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px'
            }}
          />
        </div>

        {/* 🕐 Hora */}
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            🕐 Hora: *
          </label>
          <input
            type="time"
            value={formData.hora}
            onChange={(e) => setFormData({ ...formData, hora: e.target.value })}
            required
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px'
            }}
          />
        </div>

        {/* 🏛️ Tipo de Trámite */}
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            🏛️ Tipo de Trámite: *
          </label>
          <select
            value={formData.tipo_tramite}
            onChange={(e) => setFormData({ ...formData, tipo_tramite: e.target.value })}
            required
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px'
            }}
          >
            <option value="">Selecciona un tipo de trámite...</option>
            {tiposTramites.map((tipo) => (
              <option key={tipo.id} value={tipo.id}>
                {tipo.nombre} ({tipo.duracion_estimada})
              </option>
            ))}
          </select>
          {formData.tipo_tramite && tiposTramites.length > 0 && (
            <p style={{
              fontSize: '12px',
              color: '#666',
              marginTop: '5px',
              fontStyle: 'italic'
            }}>
              {tiposTramites.find(t => t.id === formData.tipo_tramite)?.descripcion}
            </p>
          )}
        </div>

        {/* ✅ Indicador de Disponibilidad */}
        {(formData.fecha && formData.hora && formData.tipo_tramite) && (
          <div style={{ marginBottom: '15px' }}>
            {checkingAvailability ? (
              <div style={{
                padding: '10px',
                backgroundColor: '#f8f9fa',
                border: '1px solid #dee2e6',
                borderRadius: '4px',
                color: '#6c757d'
              }}>
                🔄 Verificando disponibilidad...
              </div>
            ) : availabilityStatus ? (
              <div style={{
                padding: '10px',
                backgroundColor: availabilityStatus.available ? '#d4edda' : '#f8d7da',
                border: `1px solid ${availabilityStatus.available ? '#c3e6cb' : '#f5c6cb'}`,
                borderRadius: '4px',
                color: availabilityStatus.available ? '#155724' : '#721c24'
              }}>
                {availabilityStatus.available ? '✅' : '❌'} {availabilityStatus.message}
              </div>
            ) : null}
          </div>
        )}

        {/* 📝 Descripción */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            📝 Descripción:
          </label>
          <textarea
            value={formData.descripcion}
            onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
            placeholder="Describe el propósito de la reservación..."
            rows={3}
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px',
              resize: 'vertical'
            }}
          />
        </div>

        {/* 🎛️ Botones */}
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
          <button
            type="button"
            onClick={onCancel}
            style={{
              padding: '10px 20px',
              backgroundColor: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            ❌ Cancelar
          </button>

          <button
            type="submit"
            disabled={availabilityStatus && !availabilityStatus.available}
            style={{
              padding: '10px 20px',
              backgroundColor: (availabilityStatus && !availabilityStatus.available)
                ? '#6c757d'
                : (editingReservation ? '#ffc107' : '#28a745'),
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: (availabilityStatus && !availabilityStatus.available) ? 'not-allowed' : 'pointer',
              opacity: (availabilityStatus && !availabilityStatus.available) ? 0.6 : 1
            }}
          >
            {editingReservation ? '✅ Actualizar' : '✅ Crear Reservación'}
          </button>
        </div>
      </form>
    </div>
  );
}
