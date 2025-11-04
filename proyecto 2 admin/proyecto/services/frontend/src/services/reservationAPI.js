import axios from 'axios';
import { mockUsers, mockReservations, delay } from './mockData';

const API_BASE = '/api/reservations';
const USE_MOCK = true;

class ReservationAPI {
  
  async getUsers() {
    if (USE_MOCK) {
      await delay(500);
      return mockUsers;
    }
    const response = await axios.get(`${API_BASE}/users`);
    return response.data;
  }

  async getReservations() {
    if (USE_MOCK) {
      await delay(500);
      return mockReservations.filter(r => r.estado !== 'cancelada');
    }
    const response = await axios.get(`${API_BASE}/reservations`);
    return response.data;
  }

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
