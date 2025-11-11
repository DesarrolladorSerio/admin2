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

export const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
