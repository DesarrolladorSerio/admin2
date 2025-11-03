import React, { useState } from "react";
import axios from "axios";

const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [err, setErr] = useState("");
    const [success, setSuccess] = useState("");


    const handleSubmit = async (e) => {
        e.preventDefault();
        setErr("");
        setSuccess("");

        try {
            // Enviar datos como JSON - mucho más simple y entendible
            const response = await axios.post("/api/token", {
                username: username,
                password: password
            });

            setSuccess("Login successful");
            console.log("Token:", response.data.access_token);

        } catch (error) {
            setErr("Login failed: " + (error.response?.data?.detail || error.message));
        }
    }; return (
        <div style={{ padding: "20px", maxWidth: "400px", margin: "0 auto" }}>
            <h2>Login</h2>
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
                    style={{ width: "100%", padding: "10px", backgroundColor: "#007bff", color: "white", border: "none" }}
                >
                    Login
                </button>
            </form>
            {success && <p style={{ color: "green" }}>{success}</p>}
            {err && <p style={{ color: "red" }}>{err}</p>}
        </div>
    );
};

export default Login;