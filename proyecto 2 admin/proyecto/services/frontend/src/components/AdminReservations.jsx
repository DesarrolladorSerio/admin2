import { useEffect, useState } from 'react';
import authAPI from '../services/authAPI';
import reservationAPI from '../services/reservationAPI';
import Swal from 'sweetalert2';

export default function AdminReservations() {
    const [reservations, setReservations] = useState([]);
    const [currentUser, setCurrentUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedReservation, setSelectedReservation] = useState(null);

    useEffect(() => {
        loadInitialData();
    }, []);

    const loadInitialData = async () => {
        setLoading(true);
        try {
            const [user, reservationsData] = await Promise.all([
                authAPI.getCurrentUser(),
                reservationAPI.getAllReservationsDetailed()
            ]);

            if (!['admin', 'employee'].includes(user.role)) {
                Swal.fire('Acceso Denegado', 'No tienes permisos para acceder a esta sección.', 'error');
                return;
            }

            setCurrentUser(user);
            setReservations(reservationsData);
        } catch (error) {
            console.error('Error loading data:', error);
            Swal.fire('Error', 'No se pudieron cargar los datos de las reservas.', 'error');
        }
        setLoading(false);
    };

    const handleDeleteReservation = async (reservationId, userInfo) => {
        const { value: reason } = await Swal.fire({
            title: `Anular la reserva de ${userInfo.usuario_nombre}`,
            input: 'text',
            inputLabel: 'Motivo de la anulación',
            inputPlaceholder: 'Ingrese el motivo de la anulación...',
            inputAttributes: {
              'aria-label': 'Ingrese el motivo de la anulación'
            },
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, anular',
            cancelButtonText: 'No, conservar',
            inputValidator: (value) => {
                if (!value) {
                  return '¡Necesitas escribir un motivo!'
                }
            }
        });

        if (!reason) {
            return;
        }

        try {
            // Asumimos que la API ahora acepta un motivo
            await reservationAPI.deleteReservation(reservationId, reason);
            setReservations(reservations.filter(r => r.id !== reservationId));
            Swal.fire('Anulada', 'La reserva ha sido anulada exitosamente.', 'success');
        } catch (error) {
            console.error('Error deleting reservation:', error);
            Swal.fire('Error', 'No se pudo anular la reserva.', 'error');
        }
    };

    const getStatusBadge = (estado) => {
        const colors = {
            'activa': 'bg-green-500',
            'cancelada': 'bg-red-500',
            'completada': 'bg-blue-500'
        };
        return (
            <span className={`px-2 py-1 text-xs font-bold text-white rounded-full ${colors[estado] || 'bg-gray-500'}`}>
                {estado.toUpperCase()}
            </span>
        );
    };

    const formatDate = (dateString) => new Date(dateString).toLocaleDateString('es-CL');

    if (loading) {
        return <div className="p-8 text-center text-lg">🔄 Cargando reservas...</div>;
    }

    return (
        <div className="container mx-auto p-4">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-gray-800">🔧 Gestión de Reservas</h1>
                <button
                    onClick={() => window.history.back()}
                    className="px-4 py-2 bg-gray-600 text-white font-semibold rounded-lg shadow-md hover:bg-gray-700 transition-colors"
                >
                    ← Volver
                </button>
            </div>

            <div className="mb-6 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div className="p-4 bg-white rounded-lg shadow">
                    <h3 className="text-gray-500">Total</h3>
                    <p className="text-2xl font-bold">{reservations.length}</p>
                </div>
                <div className="p-4 bg-white rounded-lg shadow">
                    <h3 className="text-gray-500">Activas</h3>
                    <p className="text-2xl font-bold text-green-600">{reservations.filter(r => r.estado === 'activa').length}</p>
                </div>
            </div>

            <div className="bg-white shadow-md rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuario</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha y Hora</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Servicio</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {reservations.map((reservation) => (
                                <tr key={reservation.id}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{reservation.id}</td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-gray-900">{reservation.usuario_nombre}</div>
                                        <div className="text-sm text-gray-500">{reservation.usuario_email || 'N/A'}</div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                                        {formatDate(reservation.fecha)} <span className="text-gray-500">{reservation.hora}</span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{reservation.tipo_tramite}</td>
                                    <td className="px-6 py-4 whitespace-nowrap">{getStatusBadge(reservation.estado)}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        <div className="flex items-center space-x-2">
                                            <button onClick={() => setSelectedReservation(reservation)} className="text-indigo-600 hover:text-indigo-900">Ver</button>
                                            {reservation.estado === 'activa' && (
                                                <button onClick={() => handleDeleteReservation(reservation.id, reservation)} className="text-red-600 hover:text-red-900">Anular</button>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {reservations.length === 0 && !loading && (
                <div className="text-center p-10 bg-gray-50 rounded-lg mt-6">
                    <h3 className="text-lg font-medium text-gray-700">📅 No hay reservas registradas</h3>
                </div>
            )}

            {selectedReservation && (
                <ReservationDetailsModal
                    reservation={selectedReservation}
                    onClose={() => setSelectedReservation(null)}
                />
            )}
        </div>
    );
}

function ReservationDetailsModal({ reservation, onClose }) {
    return (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center z-50">
            <div className="relative mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
                <div className="flex justify-between items-center pb-3 border-b">
                    <h3 className="text-lg font-medium">📋 Detalles de Reserva #{reservation.id}</h3>
                    <button onClick={onClose} className="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm p-1.5 ml-auto inline-flex items-center">
                        ✕
                    </button>
                </div>
                <div className="mt-4 space-y-2 text-sm text-gray-700">
                    <p><strong>👤 Usuario:</strong> {reservation.usuario_nombre}</p>
                    <p><strong>🆔 ID Usuario:</strong> {reservation.usuario_id}</p>
                    <p><strong>📧 Email:</strong> {reservation.usuario_email || 'No disponible'}</p>
                    <p><strong>📅 Fecha:</strong> {new Date(reservation.fecha).toLocaleDateString('es-CL')}</p>
                    <p><strong>🕒 Hora:</strong> {reservation.hora}</p>
                    <p><strong>📋 Servicio:</strong> {reservation.tipo_tramite}</p>
                    <p><strong>📝 Descripción:</strong> {reservation.descripcion || 'Sin descripción'}</p>
                    <p><strong>📊 Estado:</strong> {reservation.estado}</p>
                    <p><strong>📆 Creada:</strong> {new Date(reservation.created_at).toLocaleString('es-CL')}</p>
                </div>
            </div>
        </div>
    );
}