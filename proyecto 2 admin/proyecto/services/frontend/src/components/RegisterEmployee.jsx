import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authAPI from '../services/authAPI';

// Componentes movidos FUERA del componente principal para evitar pérdida de foco
const InputField = ({ label, type = 'text', name, value, onChange, required = true, ...props }) => (
    <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            {label} {required && '*'}
        </label>
        <input
            type={type}
            name={name}
            value={value}
            onChange={onChange}
            required={required}
            style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px'
            }}
            {...props}
        />
    </div>
);

const SelectField = ({ label, name, value, onChange, options, required = true }) => (
    <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            {label} {required && '*'}
        </label>
        <select
            name={name}
            value={value}
            onChange={onChange}
            required={required}
            style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px'
            }}
        >
            {options.map(option => (
                <option key={option.value} value={option.value}>
                    {option.label}
                </option>
            ))}
        </select>
    </div>
);

// Principio de Responsabilidad Única: Este componente se encarga únicamente del registro de empleados
export default function RegisterEmployee() {
    const navigate = useNavigate();

    // Estado del formulario usando el Principio de Separación de Responsabilidades
    const [formData, setFormData] = useState({
        email: '',
        nombre: '',
        rut: '',
        password: '',
        cargo: '',
        departamento: '',
        fecha_ingreso: '',
        tipo_contrato: 'planta'
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    // Principio de Inversión de Dependencias: Delegamos la validación a funciones especializadas
    const validateForm = () => {
        const errors = [];

        if (!formData.email || !formData.email.includes('@')) {
            errors.push('Email válido es requerido');
        }

        if (!formData.nombre || formData.nombre.length < 3) {
            errors.push('Nombre debe tener al menos 3 caracteres');
        }

        if (!formData.rut || formData.rut.length < 9) {
            errors.push('RUT válido es requerido');
        }

        if (!formData.password || formData.password.length < 8) {
            errors.push('Contraseña debe tener al menos 8 caracteres');
        }

        if (!formData.cargo) {
            errors.push('Cargo es requerido');
        }

        if (!formData.departamento) {
            errors.push('Departamento es requerido');
        }

        if (!formData.fecha_ingreso) {
            errors.push('Fecha de ingreso es requerida');
        }

        return errors;
    };

    // Principio de Responsabilidad Única: función especializada en manejo de cambios
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));

        // Limpiar errores cuando el usuario empiece a escribir
        if (error) setError('');
    };

    // Principio de Responsabilidad Única: función especializada en el envío del formulario
    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validar formulario
        const validationErrors = validateForm();
        if (validationErrors.length > 0) {
            setError(validationErrors.join(', '));
            return;
        }

        setLoading(true);
        setError('');

        try {
            // Usar el authAPI para registro de empleados
            await authAPI.registerEmployee(formData);

            setSuccess('Empleado registrado exitosamente');

            // Limpiar formulario después de registro exitoso
            setFormData({
                email: '',
                nombre: '',
                rut: '',
                password: '',
                cargo: '',
                departamento: '',
                fecha_ingreso: '',
                tipo_contrato: 'planta'
            });

            // Redirigir después de 2 segundos
            setTimeout(() => {
                navigate('/menu');
            }, 2000);

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px', maxWidth: '600px', margin: '20px auto' }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
                <button
                    onClick={() => navigate('/menu')}
                    style={{
                        background: '#6c757d',
                        color: 'white',
                        border: 'none',
                        padding: '8px 12px',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        marginRight: '15px'
                    }}
                >
                    ← Volver
                </button>
                <h1>👥 Registrar Empleado Municipal</h1>
            </div>

            {error && (
                <div style={{
                    background: '#f8d7da',
                    color: '#721c24',
                    padding: '12px',
                    borderRadius: '4px',
                    marginBottom: '20px',
                    border: '1px solid #f5c6cb'
                }}>
                    {error}
                </div>
            )}

            {success && (
                <div style={{
                    background: '#d4edda',
                    color: '#155724',
                    padding: '12px',
                    borderRadius: '4px',
                    marginBottom: '20px',
                    border: '1px solid #c3e6cb'
                }}>
                    {success}
                </div>
            )}

            <form onSubmit={handleSubmit} style={{
                background: '#f8f9fa',
                padding: '20px',
                borderRadius: '8px',
                border: '1px solid #e9ecef'
            }}>
                <h3 style={{ marginBottom: '20px', color: '#495057' }}>Información Personal</h3>

                <InputField
                    label="📧 Email"
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="empleado@municipalidad.cl"
                />

                <InputField
                    label="👤 Nombre Completo"
                    name="nombre"
                    value={formData.nombre}
                    onChange={handleInputChange}
                    placeholder="Ej: Juan Pérez González"
                />

                <InputField
                    label="🆔 RUT"
                    name="rut"
                    value={formData.rut}
                    onChange={handleInputChange}
                    placeholder="12345678-9"
                />

                <InputField
                    label="🔒 Contraseña"
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="Mínimo 8 caracteres"
                />

                <h3 style={{ marginBottom: '20px', marginTop: '30px', color: '#495057' }}>
                    Información Laboral
                </h3>

                <InputField
                    label="💼 Cargo"
                    name="cargo"
                    value={formData.cargo}
                    onChange={handleInputChange}
                    placeholder="Ej: Analista de Sistemas"
                />

                <InputField
                    label="🏢 Departamento"
                    name="departamento"
                    value={formData.departamento}
                    onChange={handleInputChange}
                    placeholder="Ej: Informática"
                />

                <InputField
                    label="📅 Fecha de Ingreso"
                    type="date"
                    name="fecha_ingreso"
                    value={formData.fecha_ingreso}
                    onChange={handleInputChange}
                />

                <SelectField
                    label="📄 Tipo de Contrato"
                    name="tipo_contrato"
                    value={formData.tipo_contrato}
                    onChange={handleInputChange}
                    options={[
                        { value: 'planta', label: 'Planta' },
                        { value: 'contrata', label: 'Contrata' },
                        { value: 'honorarios', label: 'Honorarios' }
                    ]}
                />

                <button
                    type="submit"
                    disabled={loading}
                    style={{
                        width: '100%',
                        padding: '12px',
                        background: loading ? '#6c757d' : '#28a745',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        fontSize: '16px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        marginTop: '20px'
                    }}
                >
                    {loading ? '⏳ Registrando...' : '✅ Registrar Empleado'}
                </button>
            </form>
        </div>
    );
}