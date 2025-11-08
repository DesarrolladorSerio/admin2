import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import Login from './Login';
import Menu from './Menu';
import Register from './Register';
import Reservas from './Reservas';
import AdminReservations from './components/AdminReservations';
import AdminRoute from './components/AdminRoute';
import DocumentsComponent from './components/DocumentsComponent';
import RegisterEmployee from './components/RegisterEmployee';

export default function App() {
  return (
    <Router>
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/menu" element={<Menu />} />
          <Route path="/reservas" element={<Reservas />} />
          <Route path="/documentos" element={<DocumentsComponent />} />
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
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  )
}