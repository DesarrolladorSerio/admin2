import { Navigate, Route, BrowserRouter as Router, Routes, useLocation } from 'react-router-dom';
import Login from './Login';
import Menu from './Menu';
import Register from './Register';
import Reservas from './Reservas';
import AdminReservations from './components/AdminReservations';
import AdminRoute from './components/AdminRoute';
import DocumentsComponent from './components/DocumentsComponent';
import RegisterEmployee from './components/RegisterEmployee';
import ChatBotWidget from './components/ChatBotWidget';
import DatosMunicipales from './components/DatosMunicipales';
import AdminReports from './components/AdminReports';

// Componente interno que usa useLocation
function AppContent() {
  const location = useLocation();

  // Función para verificar si el usuario está autenticado
  const isAuthenticated = () => {
    return localStorage.getItem('authToken') || localStorage.getItem('token');
  };

  // Función para verificar si estamos en páginas de login/register
  const isAuthPage = () => {
    return location.pathname === '/login' || location.pathname === '/register';
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/menu" element={<Menu />} />
        <Route path="/reservas" element={<Reservas />} />
        <Route path="/documentos" element={<DocumentsComponent />} />
        <Route path="/datos-municipales" element={<DatosMunicipales />} />
        <Route path="/admin/register-employee" element={
          <AdminRoute>
            <RegisterEmployee />
          </AdminRoute>
        } />
        <Route path="/admin/reservas" element={
          <AdminRoute allowEmployee={true}>
            <AdminReservations />
          </AdminRoute>
        } />
        <Route path="/admin/reports" element={
          <AdminRoute>
            <AdminReports />
          </AdminRoute>
        } />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>

      {/* ChatBot Widget - Solo visible para usuarios autenticados */}
      {isAuthenticated() && !isAuthPage() && <ChatBotWidget key={location.pathname} />}
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}