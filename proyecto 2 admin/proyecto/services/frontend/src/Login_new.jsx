import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const Login = () => {
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [err, setErr] = useState("");
    const [success, setSuccess] = useState("");
    const [isLogin, setIsLogin] = useState(true); // true = login, false = register

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErr("");
        setSuccess("");

        try {
            const endpoint = isLogin ? "/api/token" : "/api/register";
            const response = await axios.post(endpoint, {
                username: username,
                password: password
            });

            // Guardar token en localStorage (usando 'authToken' para consistencia)
            localStorage.setItem("authToken", response.data.access_token);

            if (isLogin) {
                setSuccess("✅ Login exitoso! Redirigiendo...");
                console.log("✅ Login exitoso. Token guardado en localStorage");
            } else {
                setSuccess("✅ Usuario registrado exitosamente! Redirigiendo...");
                console.log("✅ Usuario registrado. Token guardado en localStorage");
            }            // Redirigir al menú después de 1 segundo
            setTimeout(() => {
                navigate("/menu");
            }, 1000);

        } catch (error) {
            if (error.response?.data?.detail) {
                setErr("❌ Error: " + error.response.data.detail);
            } else {
                setErr("❌ Error: " + error.message);
            }
            console.error("❌ Error en login/registro:", error);
        }
    };

    return (
        <div style={{
            padding: "20px",
            maxWidth: "400px",
            margin: "50px auto",
            border: "1px solid #ddd",
            borderRadius: "8px",
            backgroundColor: "#f9f9f9"
        }}>
            <h2 style={{ textAlign: "center", marginBottom: "20px" }}>
                {isLogin ? "🔐 Iniciar Sesión" : "📝 Registrar Usuario"}
            </h2>

            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: "15px" }}>
                    <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                        Usuario:
                    </label>
                    <input
                        type="text"
                        placeholder="Ingresa tu usuario"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        style={{
                            width: "100%",
                            padding: "10px",
                            border: "1px solid #ccc",
                            borderRadius: "4px",
                            fontSize: "14px"
                        }}
                        required
                    />
                </div>

                <div style={{ marginBottom: "15px" }}>
                    <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                        Contraseña:
                    </label>
                    <input
                        type="password"
                        placeholder="Ingresa tu contraseña"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={{
                            width: "100%",
                            padding: "10px",
                            border: "1px solid #ccc",
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
                        padding: "12px",
                        backgroundColor: isLogin ? "#007bff" : "#28a745",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        fontSize: "16px",
                        cursor: "pointer"
                    }}
                >
                    {isLogin ? "🔑 Iniciar Sesión" : "✨ Registrar"}
                </button>
            </form>

            <div style={{ textAlign: "center", marginTop: "15px" }}>
                <button
                    type="button"
                    onClick={() => {
                        setIsLogin(!isLogin);
                        setErr("");
                        setSuccess("");
                    }}
                    style={{
                        background: "none",
                        border: "none",
                        color: "#007bff",
                        textDecoration: "underline",
                        cursor: "pointer"
                    }}
                >
                    {isLogin ? "¿No tienes cuenta? Registrate" : "¿Ya tienes cuenta? Inicia sesión"}
                </button>
            </div>

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
        </div>
    );
};

export default Login;