import { useEffect, useState } from 'react';
import authAPI from '../services/authAPI';
import reservationAPI from '../services/reservationAPI';

/**
 * 📋 Formulario de Reservas Mejorado
 * 
 * Implementa:
 * - RF02: Consulta a bases de datos municipales
 * - RF03: Autorrelleno de datos del usuario
 * - RF05: Validación de requisitos por tipo de trámite
 * 
 * Basado en TTR de la Municipalidad de Linares
 */
export default function ReservationFormNew({
    currentUser,
    editingReservation,
    onSubmit,
    onCancel
}) {
    // =========================================================================
    // ESTADOS
    // =========================================================================

    const [step, setStep] = useState(1); // Paso actual del formulario (1-4)

    const [formData, setFormData] = useState({
        // Datos de reserva
        fecha: '',
        hora: '',
        categoria_tramite: '', // primer_otorgamiento, renovacion, etc.
        tipo_tramite: '',
        descripcion: '',

        // Datos personales (RF03: Autorrelleno)
        rut: '',
        nombre: '',
        email: '',
        telefono: '',
        direccion: '',

        // Para admin/empleados
        selectedUserId: null,
        selectedUserName: ''
    });

    const [datosMunicipales, setDatosMunicipales] = useState(null);
    const [loadingDatosMunicipales, setLoadingDatosMunicipales] = useState(false);

    const [tiposTramites, setTiposTramites] = useState([]);
    const [tiposTramitesFiltrados, setTiposTramitesFiltrados] = useState([]);

    const [validacionRequisitos, setValidacionRequisitos] = useState(null);
    const [loadingValidacion, setLoadingValidacion] = useState(false);

    const [availabilityStatus, setAvailabilityStatus] = useState(null);
    const [checkingAvailability, setCheckingAvailability] = useState(false);

    const [availableUsers, setAvailableUsers] = useState([]);
    const [loadingUsers, setLoadingUsers] = useState(false);

    const isAdminOrEmployee = currentUser && ['admin', 'employee'].includes(currentUser.role);

    // =========================================================================
    // CATEGORÍAS DE TRÁMITES
    // =========================================================================

    const categoriasTramites = [
        {
            id: 'primer_otorgamiento',
            nombre: '🆕 Primer Otorgamiento - No Profesional',
            descripcion: 'Primera licencia para uso particular (Clase B, C, CR, D, E, F)'
        },
        {
            id: 'primer_otorgamiento_profesional',
            nombre: '👔 Primer Otorgamiento - Profesional',
            descripcion: 'Primera licencia profesional (Clase A1-A5: taxis, buses, camiones)'
        },
        {
            id: 'renovacion',
            nombre: '🔄 Renovación de Licencia',
            descripcion: 'Renovar licencia vigente o vencida'
        },
        {
            id: 'duplicado',
            nombre: '📄 Duplicado',
            descripcion: 'Solicitar duplicado por pérdida o robo'
        },
        {
            id: 'canje',
            nombre: '🌍 Canje Licencia Extranjera',
            descripcion: 'Canjear licencia extranjera por chilena'
        },
        {
            id: 'modificacion',
            nombre: '✏️ Modificaciones',
            descripcion: 'Cambio de domicilio, restricción, etc.'
        },
        {
            id: 'especial',
            nombre: '⭐ Trámites Especiales',
            descripcion: 'Licencia diplomático, casos especiales'
        },
        {
            id: 'otros',
            nombre: '📋 Otros Trámites Municipales',
            descripcion: 'Permisos, patentes, certificados, etc.'
        }
    ];

    // =========================================================================
    // EFECTOS
    // =========================================================================

    useEffect(() => {
        loadTiposTramites();
        if (isAdminOrEmployee) {
            loadAvailableUsers();
        }

        // RF03: Autorrelleno de datos del usuario
        if (!editingReservation && currentUser) {
            autoFillUserData();
        }
    }, [currentUser, isAdminOrEmployee]);

    useEffect(() => {
        if (editingReservation) {
            // Cargar datos de reserva existente
            setFormData({
                ...formData,
                fecha: editingReservation.fecha,
                hora: editingReservation.hora.slice(0, 5),
                tipo_tramite: editingReservation.tipo_tramite || '',
                descripcion: editingReservation.descripcion,
                selectedUserId: editingReservation.usuario_id,
                selectedUserName: editingReservation.usuario_nombre
            });
            setStep(2); // Ir al paso de selección de tipo
        }
    }, [editingReservation]);

    useEffect(() => {
        // Filtrar tipos de trámites por categoría seleccionada
        if (formData.categoria_tramite) {
            const filtrados = tiposTramites.filter(
                t => t.categoria === formData.categoria_tramite
            );
            console.log('🔍 Filtrando por categoría:', formData.categoria_tramite);
            console.log('📋 Tipos disponibles:', tiposTramites.length);
            console.log('✅ Tipos filtrados:', filtrados.length, filtrados);
            setTiposTramitesFiltrados(filtrados);
        } else {
            setTiposTramitesFiltrados([]);
        }
    }, [formData.categoria_tramite, tiposTramites]);

    useEffect(() => {
        // Verificar disponibilidad cuando cambien fecha/hora/tipo
        const delayTimer = setTimeout(() => {
            if (formData.fecha && formData.hora && formData.tipo_tramite) {
                checkAvailability();
            }
        }, 500);

        return () => clearTimeout(delayTimer);
    }, [formData.fecha, formData.hora, formData.tipo_tramite]);

    useEffect(() => {
        // RF05: Validar requisitos cuando se seleccione tipo de trámite
        if (formData.tipo_tramite && datosMunicipales) {
            validarRequisitos();
        }
    }, [formData.tipo_tramite, datosMunicipales]);

    // =========================================================================
    // FUNCIONES
    // =========================================================================

    const loadTiposTramites = async () => {
        try {
            const tipos = await reservationAPI.getTiposTramites();
            console.log('✅ Tipos de trámites cargados:', tipos);
            setTiposTramites(tipos);
        } catch (error) {
            console.error('❌ Error cargando tipos de trámites:', error);
        }
    };

    const loadAvailableUsers = async () => {
        setLoadingUsers(true);
        try {
            const users = await authAPI.getUsers();
            setAvailableUsers(users);
        } catch (error) {
            console.error('❌ Error cargando usuarios:', error);
        } finally {
            setLoadingUsers(false);
        }
    };

    /**
     * RF03: AUTORRELLENO DE DATOS
     * Carga automáticamente datos del usuario desde:
     * 1. Sesión actual (RUT, nombre, email)
     * 2. Datos municipales (dirección, teléfono)
     */
    const autoFillUserData = async () => {
        try {
            // Llenar desde sesión
            setFormData(prev => ({
                ...prev,
                rut: currentUser.rut || '',
                nombre: currentUser.nombre || currentUser.username || '',
                email: currentUser.email || '',
                telefono: currentUser.telefono || '',
                direccion: currentUser.direccion || ''
            }));

            // Cargar datos municipales para completar información faltante
            setLoadingDatosMunicipales(true);
            const response = await authAPI.consultarDatosMunicipales();

            if (response.success) {
                setDatosMunicipales(response.datos_municipales);

                // Autocompletar dirección desde permisos de edificación si existe
                const permisos = response.datos_municipales.permisos_edificacion || [];
                if (permisos.length > 0 && !formData.direccion) {
                    setFormData(prev => ({
                        ...prev,
                        direccion: permisos[0].direccion || ''
                    }));
                }

                console.log('✅ Datos municipales cargados para autorrelleno');
            }
        } catch (error) {
            console.error('⚠️ Error al cargar datos municipales:', error);
            // No es crítico, continuar con los datos de sesión
        } finally {
            setLoadingDatosMunicipales(false);
        }
    };

    /**
     * RF05: VALIDACIÓN DE REQUISITOS
     * Valida si el usuario cumple los requisitos para el tipo de trámite seleccionado
     */
    const validarRequisitos = async () => {
        if (!formData.tipo_tramite) return;

        setLoadingValidacion(true);
        try {
            const resultado = await reservationAPI.validarRequisitos(
                formData.tipo_tramite,
                formData.selectedUserId || currentUser.id
            );

            setValidacionRequisitos(resultado);

            if (!resultado.puede_realizar) {
                console.warn('⚠️ Usuario no cumple requisitos para este trámite');
            }
        } catch (error) {
            console.error('❌ Error validando requisitos:', error);
            setValidacionRequisitos(null);
        } finally {
            setLoadingValidacion(false);
        }
    };

    const checkAvailability = async () => {
        if (!formData.fecha || !formData.hora || !formData.tipo_tramite) {
            setAvailabilityStatus(null);
            return;
        }

        setCheckingAvailability(true);
        try {
            const reservationId = editingReservation ? editingReservation.id : null;
            const result = await reservationAPI.checkAvailability(
                formData.fecha,
                formData.hora,
                formData.tipo_tramite,
                reservationId
            );
            setAvailabilityStatus(result);
        } catch (error) {
            console.error('❌ Error checking availability:', error);
            setAvailabilityStatus({ available: false, message: 'Error al verificar disponibilidad' });
        } finally {
            setCheckingAvailability(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validaciones
        if (!formData.fecha || !formData.hora || !formData.tipo_tramite) {
            alert('❌ Por favor completa la fecha, hora y tipo de trámite');
            return;
        }

        // Verificar disponibilidad
        if (availabilityStatus && !availabilityStatus.available) {
            alert(`❌ ${availabilityStatus.message}`);
            return;
        }

        // Verificar requisitos (RF05)
        if (validacionRequisitos && !validacionRequisitos.puede_realizar) {
            const bloqueantes = validacionRequisitos.bloqueantes.join('\n');
            alert(`❌ No puede realizar este trámite:\n\n${bloqueantes}`);
            return;
        }

        // Validar que se haya seleccionado un usuario (para admin/empleados)
        if (isAdminOrEmployee && !formData.selectedUserId) {
            alert('❌ Por favor selecciona un usuario para la reserva');
            return;
        }

        // Preparar datos para enviar
        const finalUserId = isAdminOrEmployee ? formData.selectedUserId : currentUser.id;
        const finalUserName = isAdminOrEmployee ? formData.selectedUserName : formData.nombre;

        const submitData = {
            fecha: formData.fecha,
            hora: formData.hora + ':00',
            tipo_tramite: formData.tipo_tramite,
            descripcion: formData.descripcion,
            usuario_id: finalUserId,
            usuario_nombre: finalUserName
        };

        onSubmit(submitData);
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleUserSelect = (userId) => {
        const user = availableUsers.find(u => u.id === userId);
        if (user) {
            setFormData(prev => ({
                ...prev,
                selectedUserId: userId,
                selectedUserName: user.nombre || user.username,
                rut: user.rut || '',
                nombre: user.nombre || user.username || '',
                email: user.email || '',
                telefono: user.telefono || '',
                direccion: user.direccion || ''
            }));
        }
    };

    const nextStep = () => {
        if (step === 1 && !formData.categoria_tramite) {
            alert('❌ Por favor selecciona una categoría de trámite');
            return;
        }
        if (step === 2 && !formData.tipo_tramite) {
            alert('❌ Por favor selecciona un tipo de trámite específico');
            return;
        }
        setStep(step + 1);
    };

    const prevStep = () => setStep(step - 1);

    // =========================================================================
    // RENDERIZADO
    // =========================================================================

    return (
        <div className="max-w-4xl mx-auto p-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
                {/* Header */}
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-gray-800 mb-2">
                        {editingReservation ? '✏️ Editar Reserva' : '📅 Nueva Reserva de Hora'}
                    </h2>

                    {/* Progress indicator */}
                    <div className="flex items-center justify-between mt-4">
                        {[1, 2, 3, 4].map(s => (
                            <div key={s} className="flex items-center flex-1">
                                <div className={`
                  w-10 h-10 rounded-full flex items-center justify-center font-bold
                  ${s === step ? 'bg-blue-600 text-white' :
                                        s < step ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'}
                `}>
                                    {s < step ? '✓' : s}
                                </div>
                                {s < 4 && (
                                    <div className={`flex-1 h-1 mx-2 ${s < step ? 'bg-green-500' : 'bg-gray-300'}`} />
                                )}
                            </div>
                        ))}
                    </div>

                    <div className="flex justify-between mt-2 text-sm text-gray-600">
                        <span>Categoría</span>
                        <span>Tipo Trámite</span>
                        <span>Fecha y Hora</span>
                        <span>Confirmar</span>
                    </div>
                </div>

                <form onSubmit={handleSubmit}>
                    {/* PASO 1: SELECCIÓN DE CATEGORÍA */}
                    {step === 1 && (
                        <div className="space-y-4">
                            <h3 className="text-lg font-semibold text-gray-700 mb-4">
                                ¿Qué tipo de trámite desea realizar?
                            </h3>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {categoriasTramites.map(cat => (
                                    <button
                                        key={cat.id}
                                        type="button"
                                        onClick={() => setFormData(prev => ({ ...prev, categoria_tramite: cat.id }))}
                                        className={`
                      p-4 border-2 rounded-lg text-left transition-all
                      ${formData.categoria_tramite === cat.id
                                                ? 'border-blue-600 bg-blue-50'
                                                : 'border-gray-300 hover:border-blue-400'}
                    `}
                                    >
                                        <div className="font-semibold text-gray-800 mb-1">{cat.nombre}</div>
                                        <div className="text-sm text-gray-600">{cat.descripcion}</div>
                                    </button>
                                ))}
                            </div>

                            <div className="flex justify-end mt-6">
                                <button
                                    type="button"
                                    onClick={nextStep}
                                    disabled={!formData.categoria_tramite}
                                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                                >
                                    Siguiente →
                                </button>
                            </div>
                        </div>
                    )}

                    {/* PASO 2: SELECCIÓN DE TIPO ESPECÍFICO */}
                    {step === 2 && (
                        <div className="space-y-4">
                            <h3 className="text-lg font-semibold text-gray-700 mb-4">
                                Seleccione el trámite específico
                            </h3>

                            {tiposTramitesFiltrados.length === 0 ? (
                                <div className="p-8 bg-gray-50 border border-gray-200 rounded-lg text-center">
                                    <div className="text-6xl mb-4">📋</div>
                                    <h4 className="text-lg font-semibold text-gray-700 mb-2">
                                        No hay trámites disponibles
                                    </h4>
                                    <p className="text-gray-600">
                                        Cargando tipos de trámites o seleccione otra categoría...
                                    </p>
                                    <p className="text-sm text-gray-500 mt-2">
                                        Total de trámites: {tiposTramites.length}
                                    </p>
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 gap-3">
                                    {tiposTramitesFiltrados.map(tipo => (
                                        <button
                                            key={tipo.id}
                                            type="button"
                                            onClick={() => setFormData(prev => ({ ...prev, tipo_tramite: tipo.id }))}
                                            className={`
                      p-4 border-2 rounded-lg text-left transition-all
                      ${formData.tipo_tramite === tipo.id
                                                    ? 'border-blue-600 bg-blue-50'
                                                    : 'border-gray-300 hover:border-blue-400'}
                    `}
                                        >
                                            <div className="flex justify-between items-start">
                                                <div>
                                                    <div className="font-semibold text-gray-800">{tipo.nombre}</div>
                                                    <div className="text-sm text-gray-600 mt-1">{tipo.descripcion}</div>
                                                </div>
                                                <span className="text-xs bg-gray-200 px-2 py-1 rounded">
                                                    {tipo.duracion_estimada}
                                                </span>
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            )}                            {/* RF05: Mostrar validación de requisitos */}
                            {loadingValidacion && (
                                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                                    <div className="flex items-center">
                                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-3"></div>
                                        <span>Verificando requisitos...</span>
                                    </div>
                                </div>
                            )}

                            {validacionRequisitos && formData.tipo_tramite && (
                                <div className="space-y-3">
                                    {/* Bloqueantes */}
                                    {validacionRequisitos.bloqueantes.length > 0 && (
                                        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                                            <h4 className="font-semibold text-red-800 mb-2">⛔ Requisitos no cumplidos:</h4>
                                            <ul className="list-disc list-inside text-red-700 text-sm space-y-1">
                                                {validacionRequisitos.bloqueantes.map((msg, idx) => (
                                                    <li key={idx}>{msg}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    {/* Advertencias */}
                                    {validacionRequisitos.advertencias.length > 0 && (
                                        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                                            <h4 className="font-semibold text-yellow-800 mb-2">⚠️ Advertencias:</h4>
                                            <ul className="list-disc list-inside text-yellow-700 text-sm space-y-1">
                                                {validacionRequisitos.advertencias.map((msg, idx) => (
                                                    <li key={idx}>{msg}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    {/* Documentos requeridos */}
                                    {validacionRequisitos.documentos_requeridos.length > 0 && (
                                        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                                            <h4 className="font-semibold text-green-800 mb-2">📄 Documentos requeridos:</h4>
                                            <ul className="list-disc list-inside text-green-700 text-sm space-y-1">
                                                {validacionRequisitos.documentos_requeridos.map((doc, idx) => (
                                                    <li key={idx}>{doc}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    {/* Puede realizar */}
                                    {validacionRequisitos.puede_realizar && (
                                        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                                            <div className="flex items-center text-green-800">
                                                <span className="text-2xl mr-2">✅</span>
                                                <span className="font-semibold">Cumple con todos los requisitos para este trámite</span>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            <div className="flex justify-between mt-6">
                                <button
                                    type="button"
                                    onClick={prevStep}
                                    className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                                >
                                    ← Atrás
                                </button>
                                <button
                                    type="button"
                                    onClick={nextStep}
                                    disabled={!formData.tipo_tramite || (validacionRequisitos && !validacionRequisitos.puede_realizar)}
                                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                                >
                                    Siguiente →
                                </button>
                            </div>
                        </div>
                    )}

                    {/* PASO 3: FECHA, HORA Y DATOS PERSONALES */}
                    {step === 3 && (
                        <div className="space-y-6">
                            <h3 className="text-lg font-semibold text-gray-700 mb-4">
                                Seleccione fecha, hora y confirme sus datos
                            </h3>

                            {/* Selector de usuario (solo admin/empleados) */}
                            {isAdminOrEmployee && (
                                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                                        👤 Seleccionar Usuario
                                    </label>
                                    <select
                                        name="selectedUserId"
                                        value={formData.selectedUserId || ''}
                                        onChange={(e) => handleUserSelect(parseInt(e.target.value))}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                        required
                                    >
                                        <option value="">Seleccione un usuario...</option>
                                        {availableUsers.map(user => (
                                            <option key={user.id} value={user.id}>
                                                {user.nombre || user.username} - {user.rut} ({user.role})
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            )}

                            {/* Fecha y Hora */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                                        📅 Fecha
                                    </label>
                                    <input
                                        type="date"
                                        name="fecha"
                                        value={formData.fecha}
                                        onChange={handleChange}
                                        min={new Date().toISOString().split('T')[0]}
                                        required
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                                        🕐 Hora
                                    </label>
                                    <input
                                        type="time"
                                        name="hora"
                                        value={formData.hora}
                                        onChange={handleChange}
                                        required
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>
                            </div>

                            {/* Estado de disponibilidad */}
                            {checkingAvailability && (
                                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
                                    <div className="flex items-center">
                                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                                        <span>Verificando disponibilidad...</span>
                                    </div>
                                </div>
                            )}

                            {availabilityStatus && (
                                <div className={`p-3 border rounded-lg text-sm ${availabilityStatus.available
                                    ? 'bg-green-50 border-green-200 text-green-800'
                                    : 'bg-red-50 border-red-200 text-red-800'
                                    }`}>
                                    {availabilityStatus.message}
                                </div>
                            )}

                            {/* RF03: Datos personales autorrellenados */}
                            <div className="border-t pt-4">
                                <h4 className="font-semibold text-gray-700 mb-3">📋 Datos Personales (Autorrellenado)</h4>

                                {loadingDatosMunicipales && (
                                    <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm mb-4">
                                        <div className="flex items-center">
                                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                                            <span>Cargando datos municipales...</span>
                                        </div>
                                    </div>
                                )}

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            RUT
                                        </label>
                                        <input
                                            type="text"
                                            name="rut"
                                            value={formData.rut}
                                            onChange={handleChange}
                                            disabled
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Nombre Completo
                                        </label>
                                        <input
                                            type="text"
                                            name="nombre"
                                            value={formData.nombre}
                                            onChange={handleChange}
                                            disabled
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Email
                                        </label>
                                        <input
                                            type="email"
                                            name="email"
                                            value={formData.email}
                                            onChange={handleChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Teléfono
                                        </label>
                                        <input
                                            type="tel"
                                            name="telefono"
                                            value={formData.telefono}
                                            onChange={handleChange}
                                            placeholder="+56912345678"
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>

                                    <div className="md:col-span-2">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Dirección
                                        </label>
                                        <input
                                            type="text"
                                            name="direccion"
                                            value={formData.direccion}
                                            onChange={handleChange}
                                            placeholder="Calle, número, comuna"
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                </div>

                                {datosMunicipales && (
                                    <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800">
                                        <span className="font-semibold">✅ Datos cargados desde bases municipales</span>
                                    </div>
                                )}
                            </div>

                            {/* Descripción adicional */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    📝 Descripción o comentarios (opcional)
                                </label>
                                <textarea
                                    name="descripcion"
                                    value={formData.descripcion}
                                    onChange={handleChange}
                                    rows="3"
                                    placeholder="Agregue cualquier información adicional relevante..."
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div className="flex justify-between mt-6">
                                <button
                                    type="button"
                                    onClick={prevStep}
                                    className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                                >
                                    ← Atrás
                                </button>
                                <button
                                    type="button"
                                    onClick={nextStep}
                                    disabled={!formData.fecha || !formData.hora || (availabilityStatus && !availabilityStatus.available)}
                                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                                >
                                    Siguiente →
                                </button>
                            </div>
                        </div>
                    )}

                    {/* PASO 4: CONFIRMACIÓN */}
                    {step === 4 && (
                        <div className="space-y-6">
                            <h3 className="text-lg font-semibold text-gray-700 mb-4">
                                Confirme su reserva
                            </h3>

                            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <div className="text-sm text-gray-600">Categoría:</div>
                                        <div className="font-semibold">
                                            {categoriasTramites.find(c => c.id === formData.categoria_tramite)?.nombre}
                                        </div>
                                    </div>

                                    <div>
                                        <div className="text-sm text-gray-600">Trámite:</div>
                                        <div className="font-semibold">
                                            {tiposTramites.find(t => t.id === formData.tipo_tramite)?.nombre}
                                        </div>
                                    </div>

                                    <div>
                                        <div className="text-sm text-gray-600">Fecha:</div>
                                        <div className="font-semibold">{formData.fecha}</div>
                                    </div>

                                    <div>
                                        <div className="text-sm text-gray-600">Hora:</div>
                                        <div className="font-semibold">{formData.hora}</div>
                                    </div>

                                    <div>
                                        <div className="text-sm text-gray-600">RUT:</div>
                                        <div className="font-semibold">{formData.rut}</div>
                                    </div>

                                    <div>
                                        <div className="text-sm text-gray-600">Nombre:</div>
                                        <div className="font-semibold">{formData.nombre}</div>
                                    </div>

                                    <div>
                                        <div className="text-sm text-gray-600">Email:</div>
                                        <div className="font-semibold">{formData.email}</div>
                                    </div>

                                    <div>
                                        <div className="text-sm text-gray-600">Teléfono:</div>
                                        <div className="font-semibold">{formData.telefono || 'No especificado'}</div>
                                    </div>

                                    {formData.direccion && (
                                        <div className="md:col-span-2">
                                            <div className="text-sm text-gray-600">Dirección:</div>
                                            <div className="font-semibold">{formData.direccion}</div>
                                        </div>
                                    )}

                                    {formData.descripcion && (
                                        <div className="md:col-span-2">
                                            <div className="text-sm text-gray-600">Descripción:</div>
                                            <div className="font-semibold">{formData.descripcion}</div>
                                        </div>
                                    )}
                                </div>

                                {/* Documentos requeridos */}
                                {validacionRequisitos && validacionRequisitos.documentos_requeridos.length > 0 && (
                                    <div className="border-t pt-4 mt-4">
                                        <div className="text-sm text-gray-600 mb-2">📄 Documentos que debe traer:</div>
                                        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                                            {validacionRequisitos.documentos_requeridos.map((doc, idx) => (
                                                <li key={idx}>{doc}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>

                            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                                <p className="text-sm text-blue-800">
                                    ℹ️ Al confirmar, recibirá un correo electrónico con los detalles de su reserva y los documentos que debe traer el día de su atención.
                                </p>
                            </div>

                            <div className="flex justify-between mt-6">
                                <button
                                    type="button"
                                    onClick={prevStep}
                                    className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                                >
                                    ← Atrás
                                </button>
                                <div className="flex gap-3">
                                    {onCancel && (
                                        <button
                                            type="button"
                                            onClick={onCancel}
                                            className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                                        >
                                            Cancelar
                                        </button>
                                    )}
                                    <button
                                        type="submit"
                                        className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold"
                                    >
                                        ✓ Confirmar Reserva
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </form>
            </div>
        </div>
    );
}
