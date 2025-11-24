import { useEffect, useState } from 'react';
import authAPI from '../services/authAPI';
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
    descripcion: '',
    selectedUserId: null, // Para admin/empleados: usuario seleccionado
    selectedUserName: ''  // Para admin/empleados: nombre del usuario seleccionado
  });

  const [tiposTramites, setTiposTramites] = useState([]);
  const [availableUsers, setAvailableUsers] = useState([]); // Lista de usuarios para admin/empleados
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [availabilityStatus, setAvailabilityStatus] = useState(null);
  const [checkingAvailability, setCheckingAvailability] = useState(false);

  // Determinar si el usuario actual puede crear reservas para otros
  const isAdminOrEmployee = currentUser && ['admin', 'employee'].includes(currentUser.role);

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

    // Cargar usuarios disponibles para admin/empleados
    const loadAvailableUsers = async () => {
      if (isAdminOrEmployee) {
        setLoadingUsers(true);
        try {
          const users = await authAPI.getUsers();
          setAvailableUsers(users);
        } catch (error) {
          console.error('Error cargando usuarios:', error);
        } finally {
          setLoadingUsers(false);
        }
      }
    };

    loadTiposTramites();
    loadAvailableUsers();

    if (editingReservation) {
      // Si estamos editando, llenamos el formulario con los datos existentes
      setFormData({
        fecha: editingReservation.fecha,
        hora: editingReservation.hora.slice(0, 5), // Formato HH:MM
        tipo_tramite: editingReservation.tipo_tramite || '',
        descripcion: editingReservation.descripcion,
        selectedUserId: editingReservation.usuario_id,
        selectedUserName: editingReservation.usuario_nombre
      });
    } else {
      // Si es una nueva reserva, usamos valores por defecto
      const today = new Date().toISOString().split('T')[0];
      const now = new Date().toTimeString().slice(0, 5);
      setFormData({
        fecha: today,
        hora: now,
        tipo_tramite: '',
        descripcion: '',
        selectedUserId: isAdminOrEmployee ? null : currentUser?.id,
        selectedUserName: isAdminOrEmployee ? '' : (currentUser?.nombre || currentUser?.username || '')
      });
    }
  }, [editingReservation, currentUser, isAdminOrEmployee]);

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

    // Validar que se haya seleccionado un usuario (para admin/empleados)
    if (isAdminOrEmployee && !formData.selectedUserId) {
      alert('❌ Por favor selecciona un usuario para la reserva');
      return;
    }

    // Preparar datos para enviar
    const finalUserId = isAdminOrEmployee ? formData.selectedUserId : currentUser.id;
    const finalUserName = isAdminOrEmployee ? formData.selectedUserName : (currentUser.nombre || currentUser.username);

    const submitData = {
      fecha: formData.fecha,
      hora: formData.hora + ':00', // Agregar segundos
      tipo_tramite: formData.tipo_tramite,
      descripcion: formData.descripcion,
      usuario_id: finalUserId,
      usuario_nombre: finalUserName
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

        {/* 👤 Selección de Usuario */}
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            👤 {isAdminOrEmployee ? 'Seleccionar Usuario: *' : 'Usuario:'}
          </label>

          {isAdminOrEmployee ? (
            // Dropdown para admin/empleados
            <select
              value={formData.selectedUserId || ''}
              onChange={(e) => {
                const selectedUser = availableUsers.find(user => user.id == e.target.value);
                setFormData({
                  ...formData,
                  selectedUserId: parseInt(e.target.value),
                  selectedUserName: selectedUser ? selectedUser.nombre : ''
                });
              }}
              required
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px'
              }}
            >
              <option value="">
                {loadingUsers ? 'Cargando usuarios...' : 'Selecciona un usuario'}
              </option>
              {availableUsers.map(user => (
                <option key={user.id} value={user.id}>
                  {user.nombre} ({user.email})
                </option>
              ))}
            </select>
          ) : (
            // Campo fijo para usuarios normales
            <p style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px',
              backgroundColor: '#e9ecef'
            }}>
              {currentUser ? (currentUser.nombre || currentUser.username) : 'Cargando...'}
            </p>
          )}
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
