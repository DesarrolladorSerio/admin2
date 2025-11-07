import React, { useState, useEffect } from 'react';
import Calendar from './components/Calendar';
import ReservationList from './components/ReservationList';
import ReservationForm from './components/ReservationForm';
import reservationAPI from './services/reservationAPI';
import authAPI from './services/authAPI';

export default function Reservas() {
  const [view, setView] = useState('calendar'); // 'calendar', 'list', 'form'
  const [reservations, setReservations] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [editingReservation, setEditingReservation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      const [user, reservationsData] = await Promise.all([
        authAPI.getCurrentUser(),
        reservationAPI.getReservations()
      ]);
      setCurrentUser(user);
      setReservations(reservationsData);
    } catch (error) {
      console.error('Error loading data:', error);
      alert('Error al cargar datos. Serás redirigido al login.');
    }
    setLoading(false);
  };

  const handleCreateReservation = async (reservationData) => {
    try {
      const newReservation = await reservationAPI.createReservation(reservationData);
      setReservations([...reservations, newReservation]);
      setView('calendar');
      alert('✅ Reservación creada exitosamente.\n📧 Se ha enviado un email de confirmación.');
    } catch (error) {
      console.error('Error creating reservation:', error);
      const errorMessage = error.response?.data?.detail || 'Error al crear reservación';
      alert(`❌ ${errorMessage}`);
    }
  };

  const handleUpdateReservation = async (id, updateData) => {
    try {
      const updatedReservation = await reservationAPI.updateReservation(id, updateData);
      setReservations(reservations.map(r => r.id === id ? updatedReservation : r));
      setEditingReservation(null);
      setView('calendar');
      alert('✅ Reservación actualizada exitosamente');
    } catch (error) {
      console.error('Error updating reservation:', error);
      const errorMessage = error.response?.data?.detail || 'Error al actualizar reservación';
      alert(`❌ ${errorMessage}`);
    }
  };

  const handleDeleteReservation = async (id) => {
    if (!window.confirm('¿Estás seguro de que quieres eliminar esta reservación?')) {
      return;
    }

    try {
      await reservationAPI.deleteReservation(id);
      setReservations(reservations.filter(r => r.id !== id));
      alert('✅ Reservación eliminada exitosamente.\n📧 Se ha enviado una notificación de cancelación.');
    } catch (error) {
      console.error('Error deleting reservation:', error);
      alert('❌ Error al eliminar reservación');
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <h2>🔄 Cargando reservaciones...</h2>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* 🎛️ Barra de navegación */}
      <div style={{
        marginBottom: '20px',
        display: 'flex',
        gap: '10px',
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        <h1 style={{ margin: 0, color: '#333' }}>🏠 Sistema de Reservaciones</h1>

        <div style={{ marginLeft: 'auto', display: 'flex', gap: '10px' }}>
          <button
            onClick={() => setView('calendar')}
            style={{
              padding: '10px 15px',
              backgroundColor: view === 'calendar' ? '#007bff' : '#f8f9fa',
              color: view === 'calendar' ? 'white' : '#333',
              border: '1px solid #ddd',
              borderRadius: '5px',
              cursor: 'pointer',
              fontWeight: view === 'calendar' ? 'bold' : 'normal'
            }}
          >
            📅 Vista Calendario
          </button>

          <button
            onClick={() => setView('list')}
            style={{
              padding: '10px 15px',
              backgroundColor: view === 'list' ? '#007bff' : '#f8f9fa',
              color: view === 'list' ? 'white' : '#333',
              border: '1px solid #ddd',
              borderRadius: '5px',
              cursor: 'pointer',
              fontWeight: view === 'list' ? 'bold' : 'normal'
            }}
          >
            📋 Lista Completa
          </button>

          <button
            onClick={() => {
              setEditingReservation(null);
              setView('form');
            }}
            style={{
              padding: '10px 15px',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            ➕ Nueva Reservación
          </button>
        </div>
      </div>

      {/* 📱 Contenido según la vista actual */}
      {view === 'calendar' && (
        <Calendar
          reservations={reservations}
          currentUser={currentUser}
          selectedDate={selectedDate}
          onDateSelect={setSelectedDate}
          onEditReservation={(reservation) => {
            setEditingReservation(reservation);
            setView('form');
          }}
          onDeleteReservation={handleDeleteReservation}
        />
      )}

      {view === 'list' && (
        <ReservationList
          reservations={reservations}
          currentUser={currentUser}
          onEditReservation={(reservation) => {
            setEditingReservation(reservation);
            setView('form');
          }}
          onDeleteReservation={handleDeleteReservation}
        />
      )}

      {view === 'form' && (
        <ReservationForm
          currentUser={currentUser}
          editingReservation={editingReservation}
          onSubmit={editingReservation ?
            (data) => handleUpdateReservation(editingReservation.id, data) :
            handleCreateReservation
          }
          onCancel={() => setView('calendar')}
        />
      )}
    </div>
  );
}
