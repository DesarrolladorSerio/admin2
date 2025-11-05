import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import authAPI from "./services/authAPI"; // Importar el nuevo servicio de autenticación

const Register = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [err, setErr] = useState("");
    const [success, setSuccess] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErr("");
        setSuccess("");

        try {
            await authAPI.register({
                username: username,
                password: password
            });
            setSuccess("✅ Usuario registrado exitosamente! Redirigiendo a login...");
            // Redirigir al usuario a la página de login después de un registro exitoso
            setTimeout(() => {
                navigate("/login");
            }, 2000);

            // Limpiar formulario después de registro exitoso
            setUsername("");
            setPassword("");

        } catch (error) {
            setErr("Registration failed: " + error.message);
        }
    };

    return (
        <div style={{ padding: "20px", maxWidth: "400px", margin: "0 auto" }}>
            <h2>Register</h2>
            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: "10px" }}>
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        style={{ width: "100%", padding: "8px" }}
                        required
                    />
                </div>
                <div style={{ marginBottom: "10px" }}>
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={{ width: "100%", padding: "8px" }}
                        required
                    />
                </div>
                <button
                    type="submit"
                    style={{ width: "100%", padding: "10px", backgroundColor: "#28a745", color: "white", border: "none" }}
                >
                    Register
                </button>
            </form>
            {success && <p style={{ color: "green" }}>{success}</p>}
            {err && <p style={{ color: "red" }}>{err}</p>}
            <p style={{ marginTop: "10px" }}>
                Already have an account? <Link to="/login">Login</Link>
            </p>
        </div>
    );
};

export default Register;
