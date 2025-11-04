import React, { useState, useEffect } from 'react';

export default function ReservationForm({ 
  users, 
  editingReservation, 
  onSubmit, 
  onCancel 
}) {
  const [formData, setFormData] = useState({
    fecha: '',
    hora: '',
    usuario_id: '',
    usuario_nombre: '',
    descripcion: ''
  });

  useEffect(() => {
    if (editingReservation) {
      setFormData({
        fecha: editingReservation.fecha,
        hora: editingReservation.hora.slice(0, 5), // HH:MM formato
        usuario_id: editingReservation.usuario_id,
        usuario_nombre: editingReservation.usuario_nombre,
        descripcion: editingReservation.descripcion
      });
    } else {
      // Valores por defecto para nueva reservación
      const today = new Date().toISOString().split('T')[0];
      const now = new Date().toTimeString().slice(0, 5);
      setFormData({
        fecha: today,
        hora: now,
        usuario_id: '',
        usuario_nombre: '',
        descripcion: ''
      });
    }
  }, [editingReservation]);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validaciones
    if (!formData.usuario_id || !formData.fecha || !formData.hora) {
      alert('❌ Por favor completa todos los campos obligatorios');
      return;
    }

    // Preparar datos para enviar
    const submitData = {
      ...formData,
      hora: formData.hora + ':00', // Agregar segundos
      usuario_id: parseInt(formData.usuario_id)
    };

    onSubmit(submitData);
  };

  const handleUserChange = (e) => {
    const userId = e.target.value;
    const user = users.find(u => u.id === parseInt(userId));
    
    setFormData({
      ...formData,
      usuario_id: userId,
      usuario_nombre: user ? user.username : ''
    });
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
        
        {/* 👤 Selector de Usuario */}
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            👤 Usuario: *
          </label>
          <select
            value={formData.usuario_id}
            onChange={handleUserChange}
            required
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px'
            }}
          >
            <option value="">Selecciona un usuario...</option>
            {users.map(user => (
              <option key={user.id} value={user.id}>
                {user.username}
              </option>
            ))}
          </select>
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
            style={{
              padding: '10px 20px',
              backgroundColor: editingReservation ? '#ffc107' : '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            {editingReservation ? '✅ Actualizar' : '✅ Crear Reservación'}
          </button>
        </div>
      </form>
    </div>
  );
}
