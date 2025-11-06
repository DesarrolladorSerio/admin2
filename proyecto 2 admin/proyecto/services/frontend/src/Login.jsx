import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import authAPI from "./services/authAPI"; // Importar el nuevo servicio de autenticación

const Login = () => {
    const [identifier, setIdentifier] = useState("");
    const [password, setPassword] = useState("");
    const [loginType, setLoginType] = useState("email"); // "email" o "rut"
    const [err, setErr] = useState("");
    const [success, setSuccess] = useState("");
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
        setErr(""); // Limpiar errores
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErr("");
        setSuccess("");

        try {
            await authAPI.login(identifier, password, loginType);
            setSuccess("✅ Inicio de sesión exitoso!");
            navigate('/menu');

        } catch (error) {
            const errorMsg = error.response?.data?.detail || error.message;
            setErr("Error en el login: " + errorMsg);
        }
    };

    return (
        <div style={{
            padding: "20px",
            maxWidth: "450px",
            margin: "50px auto",
            backgroundColor: "white",
            borderRadius: "8px",
            boxShadow: "0 2px 10px rgba(0,0,0,0.1)"
        }}>
            <h2 style={{ textAlign: "center", marginBottom: "30px", color: "#333" }}>
                🔐 Iniciar Sesión
            </h2>

            {/* Toggle de tipo de login */}
            <div style={{
                marginBottom: "20px",
                textAlign: "center",
                padding: "15px",
                backgroundColor: "#f8f9fa",
                borderRadius: "6px",
                border: "1px solid #e9ecef"
            }}>
                <p style={{ marginBottom: "10px", fontWeight: "bold", color: "#495057" }}>
                    Tipo de inicio de sesión:
                </p>
                <button
                    type="button"
                    onClick={toggleLoginType}
                    style={{
                        padding: "10px 20px",
                        backgroundColor: loginType === "email" ? "#007bff" : "#6c757d",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                        fontSize: "14px",
                        fontWeight: "bold",
                        transition: "background-color 0.3s"
                    }}
                >
                    {loginType === "email" ? "📧 Ingresar con Email" : "🆔 Ingresar con RUT"}
                </button>
                <p style={{ marginTop: "8px", fontSize: "12px", color: "#6c757d" }}>
                    {loginType === "email"
                        ? "Haz clic para cambiar a RUT"
                        : "Haz clic para cambiar a Email"
                    }
                </p>
            </div>

            <form onSubmit={handleSubmit}>
                {/* Campo de identificador (Email o RUT) */}
                <div style={{ marginBottom: "15px" }}>
                    <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                        {loginType === "email" ? "📧 Email:" : "🆔 RUT:"}
                    </label>
                    <input
                        type={loginType === "email" ? "email" : "text"}
                        placeholder={loginType === "email" ? "ejemplo@correo.com" : "12.345.678-9"}
                        value={identifier}
                        onChange={handleIdentifierChange}
                        style={{
                            width: "100%",
                            padding: "12px",
                            border: "1px solid #ddd",
                            borderRadius: "4px",
                            fontSize: "14px"
                        }}
                        required
                        maxLength={loginType === "rut" ? "12" : undefined}
                    />
                </div>

                {/* Campo de contraseña */}
                <div style={{ marginBottom: "20px" }}>
                    <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                        🔒 Contraseña:
                    </label>
                    <input
                        type="password"
                        placeholder="Ingresa tu contraseña"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={{
                            width: "100%",
                            padding: "12px",
                            border: "1px solid #ddd",
                            borderRadius: "4px",
                            fontSize: "14px"
                        }}
                        required
                    />
                </div>

                <button
                    type="submit"
                    style={{
                        width: "100%",
                        padding: "15px",
                        backgroundColor: "#007bff",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        fontSize: "16px",
                        fontWeight: "bold",
                        cursor: "pointer"
                    }}
                >
                    🔐 Iniciar Sesión
                </button>
            </form>

            {success && (
                <div style={{
                    color: "green",
                    marginTop: "15px",
                    padding: "10px",
                    backgroundColor: "#d4edda",
                    border: "1px solid #c3e6cb",
                    borderRadius: "4px"
                }}>
                    {success}
                </div>
            )}

            {err && (
                <div style={{
                    color: "red",
                    marginTop: "15px",
                    padding: "10px",
                    backgroundColor: "#f8d7da",
                    border: "1px solid #f5c6cb",
                    borderRadius: "4px"
                }}>
                    {err}
                </div>
            )}

            <p style={{ marginTop: "20px", textAlign: "center" }}>
                ¿No tienes una cuenta?{" "}
                <Link
                    to="/register"
                    style={{ color: "#28a745", textDecoration: "none", fontWeight: "bold" }}
                >
                    Registrarse
                </Link>
            </p>
        </div>
    );
};

export default Login;
