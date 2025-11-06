import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import authAPI from "./services/authAPI"; // Importar el nuevo servicio de autenticación

const Register = () => {
    const [email, setEmail] = useState("");
    const [nombre, setNombre] = useState("");
    const [rut, setRut] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [err, setErr] = useState("");
    const [success, setSuccess] = useState("");
    const navigate = useNavigate();

    // Función para validar formato de RUT chileno
    const validateRUT = (rut) => {
        if (!rut) return false; // RUT es obligatorio
        const cleanRUT = rut.replace(/[.-]/g, '');
        return /^\d{7,8}[0-9Kk]$/.test(cleanRUT);
    };

    // Función para formatear RUT mientras se escribe
    const formatRUT = (value) => {
        const cleaned = value.replace(/[^0-9Kk]/g, '').toUpperCase();
        if (cleaned.length <= 1) return cleaned;
        if (cleaned.length <= 8) {
            return cleaned.slice(0, -1) + '-' + cleaned.slice(-1);
        }
        return cleaned.slice(0, -1).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.') + '-' + cleaned.slice(-1);
    };

    const handleRUTChange = (e) => {
        const formatted = formatRUT(e.target.value);
        setRut(formatted);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErr("");
        setSuccess("");

        // Validaciones
        if (password !== confirmPassword) {
            setErr("Las contraseñas no coinciden");
            return;
        }

        if (password.length < 8) {
            setErr("La contraseña debe tener al menos 8 caracteres");
            return;
        }

        if (!validateRUT(rut)) {
            setErr("RUT es obligatorio y debe tener formato válido (ej: 12.345.678-9)");
            return;
        }

        try {
            await authAPI.register({
                email: email,
                nombre: nombre,
                rut: rut,
                password: password
            });
            setSuccess("✅ Usuario registrado exitosamente! Redirigiendo al menú...");

            // Redirigir al menú después de registro exitoso (ya que el login es automático)
            setTimeout(() => {
                navigate("/menu");
            }, 2000);

            // Limpiar formulario
            setEmail("");
            setNombre("");
            setRut("");
            setPassword("");
            setConfirmPassword("");

        } catch (error) {
            setErr("Error en el registro: " + error.message);
        }
    };

    return (
        <div style={{
            padding: "20px",
            maxWidth: "500px",
            margin: "50px auto",
            backgroundColor: "white",
            borderRadius: "8px",
            boxShadow: "0 2px 10px rgba(0,0,0,0.1)"
        }}>
            <h2 style={{ textAlign: "center", marginBottom: "30px", color: "#333" }}>
                📝 Registro de Usuario
            </h2>
            <form onSubmit={handleSubmit}>
                {/* Email */}
                <div style={{ marginBottom: "15px" }}>
                    <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                        📧 Email: *
                    </label>
                    <input
                        type="email"
                        placeholder="ejemplo@correo.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
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

                {/* Nombre */}
                <div style={{ marginBottom: "15px" }}>
                    <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                        👤 Nombre Completo: *
                    </label>
                    <input
                        type="text"
                        placeholder="Juan Pérez García"
                        value={nombre}
                        onChange={(e) => setNombre(e.target.value)}
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

                {/* RUT */}
                <div style={{ marginBottom: "15px" }}>
                    <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                        🆔 RUT: *
                    </label>
                    <input
                        type="text"
                        placeholder="12.345.678-9"
                        value={rut}
                        onChange={handleRUTChange}
                        style={{
                            width: "100%",
                            padding: "12px",
                            border: "1px solid #ddd",
                            borderRadius: "4px",
                            fontSize: "14px"
                        }}
                        maxLength="12"
                        required
                    />
                    <small style={{ color: "#666", fontSize: "12px" }}>
                        Formato: 12.345.678-9 (requerido para login)
                    </small>
                </div>

                {/* Contraseña */}
                <div style={{ marginBottom: "15px" }}>
                    <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                        🔒 Contraseña: *
                    </label>
                    <input
                        type="password"
                        placeholder="Mínimo 8 caracteres"
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
                        minLength="8"
                    />
                </div>

                {/* Confirmar Contraseña */}
                <div style={{ marginBottom: "20px" }}>
                    <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                        🔒 Confirmar Contraseña: *
                    </label>
                    <input
                        type="password"
                        placeholder="Repetir contraseña"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
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
                        backgroundColor: "#28a745",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        fontSize: "16px",
                        fontWeight: "bold",
                        cursor: "pointer"
                    }}
                >
                    📝 Registrarse
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
                ¿Ya tienes una cuenta?{" "}
                <Link
                    to="/login"
                    style={{ color: "#007bff", textDecoration: "none", fontWeight: "bold" }}
                >
                    Iniciar Sesión
                </Link>
            </p>
        </div>
    );
};

export default Register;
