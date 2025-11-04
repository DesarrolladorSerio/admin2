import React, { useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

const Register = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [err, setErr] = useState("");
    const [success, setSuccess] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErr("");
        setSuccess("");

        try {
            const response = await axios.post("http://localhost:8001/register", {
                username: username,
                password: password
            });

            setSuccess("✅ Usuario registrado exitosamente! Token: " + response.data.access_token.substring(0, 20) + "...");
            console.log("Token completo:", response.data.access_token);

            // Limpiar formulario después de registro exitoso
            setUsername("");
            setPassword("");

        } catch (error) {
            setErr("Registration failed: " + (error.response?.data?.detail || error.message));
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
