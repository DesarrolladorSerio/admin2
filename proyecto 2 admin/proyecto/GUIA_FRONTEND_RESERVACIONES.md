# 🎨 Guía Frontend: Integración con API de Reservaciones

## 🎯 Objetivo
Esta guía está diseñada para que puedas desarrollar el frontend de reservaciones **SIN necesidad de tener la API funcionando**. Incluye mocks, esquemas visuales y ejemplos completos.

---

## 📋 Estructura de Datos de la API

### 👤 Usuario (UserResponse)
```javascript
{
  "id": 1,
  "username": "admin@municipalidad.cl"
}
```

### 📅 Reservación (ReservationResponse)
```javascript
{
  "id": 1,
  "fecha": "2025-11-10",           // YYYY-MM-DD
  "hora": "14:30:00",              // HH:MM:SS
  "usuario_id": 1,
  "usuario_nombre": "admin@municipalidad.cl",
  "descripcion": "Reunión importante",
  "estado": "activa",              // activa, cancelada, completada
  "created_at": "2025-11-04T10:30:00Z"
}
```

---

## 🔌 Endpoints de la API

### Base URL: `/api/reservations/`

| Método | Endpoint | Descripción | Uso en Frontend |
|--------|----------|-------------|-----------------|
| `GET` | `/users` | Lista todos los usuarios | Dropdown de usuarios |
| `GET` | `/reservations` | Lista todas las reservaciones | Vista admin/lista completa |
| `POST` | `/reservations` | Crea nueva reservación | Formulario de crear |
| `GET` | `/reservations/{id}` | Obtiene reservación específica | Ver detalles |
| `PUT` | `/reservations/{id}` | Actualiza reservación | Formulario de editar |
| `DELETE` | `/reservations/{id}` | Elimina reservación | Botón eliminar |
| `GET` | `/reservations/calendar/{start}/{end}` | Reservaciones por rango | Vista calendario |

---

## 🎨 Diseño de Pantallas

### 📱 Pantalla Principal de Reservas
```
┌─────────────────────────────────────────────────────────┐
│  🏠 SISTEMA DE RESERVACIONES                            │
│                                                         │
│  [📅 Vista Calendario] [📋 Lista Completa] [➕ Nuevo]    │
│                                                         │
│  ┌─── Calendario Mensual ────────────────────────────┐  │
│  │  Lu  Ma  Mi  Ju  Vi  Sa  Do                      │  │
│  │   1   2   3   4   5   6   7                      │  │
│  │   8   9  [10] 11  12  13  14  ← (10 tiene reserva)│  │
│  │  15  16  17  18  19  20  21                      │  │
│  │  ...                                              │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  📅 Reservaciones del día seleccionado:                 │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 🕐 14:30 - admin@municipalidad.cl              │    │
│  │    "Reunión importante"                         │    │
│  │    [✏️ Editar] [🗑️ Eliminar]                     │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### ➕ Modal/Pantalla de Crear Reservación
```
┌─────────────────────────────────────────┐
│  ➕ Nueva Reservación                    │
│                                         │
│  👤 Usuario:                            │
│  [🔽 Dropdown con usuarios ▼]           │
│                                         │
│  📅 Fecha:                              │
│  [📅 Date Picker]                       │
│                                         │
│  🕐 Hora:                               │
│  [🕐 Time Picker]                       │
│                                         │
│  📝 Descripción:                        │
│  [                                   ]  │
│  [                                   ]  │
│                                         │
│  [❌ Cancelar] [✅ Guardar Reservación]   │
└─────────────────────────────────────────┘
```

### 📋 Lista Completa de Reservaciones
```
┌─────────────────────────────────────────────────────────┐
│  📋 Todas las Reservaciones                             │
│                                                         │
│  🔍 [Buscar...]               [🗓️ Filtrar por fecha]    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 📅 2025-11-10 🕐 14:30                         │    │
│  │ 👤 admin@municipalidad.cl                      │    │
│  │ 📝 "Reunión importante"                        │    │
│  │ 🏷️ Estado: ● Activa                            │    │
│  │ [✏️ Editar] [🗑️ Eliminar] [👁️ Ver Detalles]      │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 📅 2025-11-11 🕐 09:00                         │    │
│  │ 👤 usuario2@empresa.com                        │    │
│  │ 📝 "Presentación proyecto"                     │    │
│  │ 🏷️ Estado: ● Activa                            │    │
│  │ [✏️ Editar] [🗑️ Eliminar] [👁️ Ver Detalles]      │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Componentes React Sugeridos

### 📁 Estructura de archivos:
```
src/
├── components/
│   ├── Reservas.jsx              # Componente principal
│   ├── Calendar.jsx              # Vista calendario
│   ├── ReservationList.jsx       # Lista de reservaciones  
│   ├── ReservationForm.jsx       # Formulario crear/editar
│   ├── ReservationCard.jsx       # Tarjeta individual
│   └── UserSelector.jsx          # Dropdown de usuarios
├── services/
│   ├── reservationAPI.js         # Llamadas a la API
│   └── mockData.js               # Datos simulados
└── utils/
    └── dateHelpers.js            # Funciones de fechas
```

---

## 🎭 Mock Data para Desarrollo

### 📄 mockData.js
```javascript
export const mockUsers = [
  { id: 1, username: "admin@municipalidad.cl" },
  { id: 2, username: "secretaria@municipalidad.cl" },
  { id: 3, username: "alcalde@municipalidad.cl" },
  { id: 4, username: "tesorero@municipalidad.cl" }
];

export const mockReservations = [
  {
    id: 1,
    fecha: "2025-11-10",
    hora: "14:30:00", 
    usuario_id: 1,
    usuario_nombre: "admin@municipalidad.cl",
    descripcion: "Reunión de presupuesto anual",
    estado: "activa",
    created_at: "2025-11-04T10:00:00Z"
  },
  {
    id: 2,
    fecha: "2025-11-10",
    hora: "16:00:00",
    usuario_id: 2, 
    usuario_nombre: "secretaria@municipalidad.cl",
    descripcion: "Revisión de documentos",
    estado: "activa",
    created_at: "2025-11-04T10:15:00Z"
  },
  {
    id: 3,
    fecha: "2025-11-11",
    hora: "09:00:00",
    usuario_id: 3,
    usuario_nombre: "alcalde@municipalidad.cl", 
    descripcion: "Sesión de consejo municipal",
    estado: "activa",
    created_at: "2025-11-04T10:30:00Z"
  },
  {
    id: 4,
    fecha: "2025-11-09",
    hora: "11:00:00",
    usuario_id: 1,
    usuario_nombre: "admin@municipalidad.cl",
    descripcion: "Reunión cancelada",
    estado: "cancelada", 
    created_at: "2025-11-03T15:00:00Z"
  }
];

// Función para simular delay de API
export const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
```

---

## 🔌 Servicio de API con Mocks

### 📄 reservationAPI.js
```javascript
import axios from 'axios';
import { mockUsers, mockReservations, delay } from './mockData';

// Configuración
const API_BASE = '/api/reservations';
const USE_MOCK = true; // Cambiar a false cuando la API esté lista

class ReservationAPI {
  
  // 👥 Obtener todos los usuarios
  async getUsers() {
    if (USE_MOCK) {
      await delay(500); // Simular latencia
      return mockUsers;
    }
    
    const response = await axios.get(`${API_BASE}/users`);
    return response.data;
  }

  // 📋 Obtener todas las reservaciones
  async getReservations() {
    if (USE_MOCK) {
      await delay(500);
      return mockReservations.filter(r => r.estado !== 'cancelada');
    }
    
    const response = await axios.get(`${API_BASE}/reservations`);
    return response.data;
  }

  // 📅 Obtener reservaciones por rango de fechas (calendario)
  async getReservationsByDateRange(startDate, endDate) {
    if (USE_MOCK) {
      await delay(500);
      return mockReservations.filter(r => {
        return r.fecha >= startDate && r.fecha <= endDate && r.estado === 'activa';
      });
    }
    
    const response = await axios.get(`${API_BASE}/reservations/calendar/${startDate}/${endDate}`);
    return response.data;
  }

  // ➕ Crear nueva reservación
  async createReservation(reservationData) {
    if (USE_MOCK) {
      await delay(800);
      const newReservation = {
        id: Math.max(...mockReservations.map(r => r.id)) + 1,
        ...reservationData,
        estado: 'activa',
        created_at: new Date().toISOString()
      };
      mockReservations.push(newReservation);
      return newReservation;
    }
    
    const response = await axios.post(`${API_BASE}/reservations`, reservationData);
    return response.data;
  }

  // ✏️ Actualizar reservación existente
  async updateReservation(id, updateData) {
    if (USE_MOCK) {
      await delay(600);
      const index = mockReservations.findIndex(r => r.id === id);
      if (index !== -1) {
        mockReservations[index] = { ...mockReservations[index], ...updateData };
        return mockReservations[index];
      }
      throw new Error('Reservación no encontrada');
    }
    
    const response = await axios.put(`${API_BASE}/reservations/${id}`, updateData);
    return response.data;
  }

  // 🗑️ Eliminar reservación
  async deleteReservation(id) {
    if (USE_MOCK) {
      await delay(400);
      const index = mockReservations.findIndex(r => r.id === id);
      if (index !== -1) {
        mockReservations[index].estado = 'cancelada';
        return { message: 'Reservación eliminada exitosamente' };
      }
      throw new Error('Reservación no encontrada');
    }
    
    const response = await axios.delete(`${API_BASE}/reservations/${id}`);
    return response.data;
  }

  // 👁️ Obtener reservación específica
  async getReservation(id) {
    if (USE_MOCK) {
      await delay(300);
      const reservation = mockReservations.find(r => r.id === id);
      if (!reservation) {
        throw new Error('Reservación no encontrada');
      }
      return reservation;
    }
    
    const response = await axios.get(`${API_BASE}/reservations/${id}`);
    return response.data;
  }
}

export default new ReservationAPI();
```

---

## 🎨 Componente Principal de Reservas

### 📄 Reservas.jsx
```javascript
import React, { useState, useEffect } from 'react';
import Calendar from './Calendar';
import ReservationList from './ReservationList';
import ReservationForm from './ReservationForm';
import reservationAPI from '../services/reservationAPI';

export default function Reservas() {
  const [view, setView] = useState('calendar'); // 'calendar', 'list', 'form'
  const [reservations, setReservations] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [editingReservation, setEditingReservation] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      const [usersData, reservationsData] = await Promise.all([
        reservationAPI.getUsers(),
        reservationAPI.getReservations()
      ]);
      setUsers(usersData);
      setReservations(reservationsData);
    } catch (error) {
      console.error('Error loading data:', error);
      alert('Error al cargar datos');
    }
    setLoading(false);
  };

  const handleCreateReservation = async (reservationData) => {
    try {
      const newReservation = await reservationAPI.createReservation(reservationData);
      setReservations([...reservations, newReservation]);
      setView('calendar');
      alert('✅ Reservación creada exitosamente');
    } catch (error) {
      console.error('Error creating reservation:', error);
      alert('❌ Error al crear reservación');
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
      alert('❌ Error al actualizar reservación');
    }
  };

  const handleDeleteReservation = async (id) => {
    if (!confirm('¿Estás seguro de que quieres eliminar esta reservación?')) {
      return;
    }
    
    try {
      await reservationAPI.deleteReservation(id);
      setReservations(reservations.filter(r => r.id !== id));
      alert('✅ Reservación eliminada exitosamente');
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
              cursor: 'pointer'
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
              cursor: 'pointer'
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
              cursor: 'pointer'
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
          onEditReservation={(reservation) => {
            setEditingReservation(reservation);
            setView('form');
          }}
          onDeleteReservation={handleDeleteReservation}
        />
      )}

      {view === 'form' && (
        <ReservationForm 
          users={users}
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
```

---

## 🗓️ Componente de Calendario

### 📄 Calendar.jsx (Versión Simple)
```javascript
import React from 'react';

export default function Calendar({ 
  reservations, 
  selectedDate, 
  onDateSelect, 
  onEditReservation, 
  onDeleteReservation 
}) {
  
  // Obtener reservaciones del día seleccionado
  const selectedDateStr = selectedDate.toISOString().split('T')[0];
  const dayReservations = reservations.filter(r => r.fecha === selectedDateStr);

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
                    🕐 {reservation.hora.slice(0, 5)} - {reservation.usuario_nombre}
                  </div>
                  <div style={{ color: '#666', marginBottom: '5px' }}>
                    📝 {reservation.descripcion}
                  </div>
                  <div style={{ fontSize: '12px', color: '#999' }}>
                    🏷️ Estado: {reservation.estado}
                  </div>
                </div>
                
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
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
```

---

## 📝 Formulario de Reservaciones

### 📄 ReservationForm.jsx
```javascript
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
```

---

## 🚀 Cómo Empezar

### 1. **Configurar el Mock**
```javascript
// En reservationAPI.js, asegúrate de que:
const USE_MOCK = true; // Mantener en true mientras desarrollas
```

### 2. **Probar el Frontend**
```bash
npm start
# El frontend funcionará con datos simulados
```

### 3. **Cuando la API esté lista**
```javascript
// Cambiar a:
const USE_MOCK = false; 
// Y probar las llamadas reales
```

---

## 🎯 Lista de Tareas para el Frontend

### ✅ Básico (Esencial)
- [ ] Crear componente `Reservas.jsx` principal
- [ ] Implementar `reservationAPI.js` con mocks
- [ ] Crear formulario de nueva reservación
- [ ] Mostrar lista simple de reservaciones
- [ ] Botones de editar/eliminar

### 🎨 Intermedio (Recomendado)
- [ ] Vista de calendario mensual
- [ ] Filtros por fecha/usuario
- [ ] Validaciones de formulario
- [ ] Estados de carga (loading)
- [ ] Confirmaciones de eliminación

### 🚀 Avanzado (Opcional)
- [ ] Calendario con librerías (react-calendar, etc.)
- [ ] Búsqueda en tiempo real
- [ ] Exportar a PDF/Excel
- [ ] Notificaciones push
- [ ] Vista semanal/diaria

---

## 🎨 Paleta de Colores Sugerida

```css
/* Colores principales */
:root {
  --primary: #007bff;      /* Azul principal */
  --success: #28a745;      /* Verde éxito */
  --warning: #ffc107;      /* Amarillo editar */
  --danger: #dc3545;       /* Rojo eliminar */
  --info: #17a2b8;         /* Azul información */
  --light: #f8f9fa;        /* Gris claro fondo */
  --dark: #343a40;         /* Gris oscuro texto */
}
```

---

## 📱 Responsive Design

### Breakpoints recomendados:
```css
/* Mobile */
@media (max-width: 768px) {
  /* Calendario en una columna */
  /* Botones más grandes */
  /* Formularios en pantalla completa */
}

/* Tablet */
@media (max-width: 1024px) {
  /* Calendario + lista lado a lado */
}

/* Desktop */
@media (min-width: 1025px) {
  /* Layout completo */
}
```

---

¡Con esta guía tu compañero puede desarrollar todo el frontend sin necesidad de que la API esté funcionando! 🚀

Los mocks le permitirán probar todas las funcionalidades y cuando la API esté lista, solo necesita cambiar `USE_MOCK = false`.