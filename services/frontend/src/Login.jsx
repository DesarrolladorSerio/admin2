import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import authAPI from "./services/authAPI"; // Importar el nuevo servicio de autenticación
import Swal from 'sweetalert2'; // Importar SweetAlert2

const Login = () => {
    const [identifier, setIdentifier] = useState("");
    const [password, setPassword] = useState("");
    const [loginType, setLoginType] = useState("email"); // "email" o "rut"
    // const [err, setErr] = useState(""); // Ya no se usa directamente
    // const [success, setSuccess] = useState(""); // Ya no se usa directamente
    const navigate = useNavigate();

    // Función para formatear RUT mientras se escribe (solo si es modo RUT)
    const formatRUT = (value) => {
        if (loginType !== "rut") return value;
        const cleaned = value.replace(/[^0-9Kk]/g, '').toUpperCase();
        if (cleaned.length <= 1) return cleaned;
        if (cleaned.length <= 8) {
            return cleaned.slice(0, -1) + '-' + cleaned.slice(-1);
        }
        return cleaned.slice(0, -1).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.') + '-' + cleaned.slice(-1);
    };

    const handleIdentifierChange = (e) => {
        if (loginType === "rut") {
            setIdentifier(formatRUT(e.target.value));
        } else {
            setIdentifier(e.target.value);
        }
    };

    const toggleLoginType = () => {
        setLoginType(loginType === "email" ? "rut" : "email");
        setIdentifier(""); // Limpiar el campo al cambiar
        // setErr(""); // Limpiar errores - ya no se usa directamente
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        // setErr(""); // Ya no se usa directamente
        // setSuccess(""); // Ya no se usa directamente

        try {
            await authAPI.login(identifier, password, loginType);
            Swal.fire({
                icon: 'success',
                title: 'Inicio de sesión exitoso!',
                text: 'Redirigiendo...',
                showConfirmButton: false,
                timer: 1500
            });
            navigate('/menu');

        } catch (error) {
            const errorMsg = error.response?.data?.detail || error.message;
            Swal.fire({
                icon: 'error',
                title: 'Error de Login',
                text: 'Error en el login: ' + errorMsg,
            });
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
            <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">
                    🔐 Iniciar Sesión
                </h2>

                {/* Toggle de tipo de login */}
                <div className="mb-6 text-center p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <p className="mb-2 font-semibold text-gray-700">
                        Tipo de inicio de sesión:
                    </p>
                    <button
                        type="button"
                        onClick={toggleLoginType}
                        className={`px-5 py-2 rounded-md text-white font-bold transition-colors duration-300 ${
                            loginType === "email" ? "bg-blue-600 hover:bg-blue-700" : "bg-gray-500 hover:bg-gray-600"
                        }`}
                    >
                        {loginType === "email" ? "📧 Ingresar con Email" : "🆔 Ingresar con RUT"}
                    </button>
                    <p className="mt-2 text-xs text-gray-500">
                        {loginType === "email"
                            ? "Haz clic para cambiar a RUT"
                            : "Haz clic para cambiar a Email"
                        }
                    </p>
                </div>

                <form onSubmit={handleSubmit}>
                    {/* Campo de identificador (Email o RUT) */}
                    <div className="mb-4">
                        <label className="block text-gray-700 text-sm font-bold mb-2">
                            {loginType === "email" ? "📧 Email:" : "🆔 RUT:"}
                        </label>
                        <input
                            type={loginType === "email" ? "email" : "text"}
                            placeholder={loginType === "email" ? "ejemplo@correo.com" : "12.345.678-9"}
                            value={identifier}
                            onChange={handleIdentifierChange}
                            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500"
                            required
                            maxLength={loginType === "rut" ? "12" : undefined}
                        />
                    </div>

                    {/* Campo de contraseña */}
                    <div className="mb-6">
                        <label className="block text-gray-700 text-sm font-bold mb-2">
                            🔒 Contraseña:
                        </label>
                        <input
                            type="password"
                            placeholder="Ingresa tu contraseña"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg w-full focus:outline-none focus:shadow-outline transition-colors duration-300"
                    >
                        🔐 Iniciar Sesión
                    </button>
                </form>

                <p className="mt-6 text-center text-gray-600">
                    ¿No tienes una cuenta?{" "}
                    <Link
                        to="/register"
                        className="text-green-600 hover:text-green-800 font-bold transition-colors duration-300"
                    >
                        Registrarse
                    </Link>
                </p>
            </div>
        </div>
    );
};

export default Login;
