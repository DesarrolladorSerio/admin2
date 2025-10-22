import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [valor, setValor] = useState(0);

  useEffect(() => {
    fetch(`${API_URL}/contador`)
      .then((res) => res.json())
      .then((data) => setValor(data.valor));
  }, []);

  const incrementar = async () => {
    const res = await fetch(`${API_URL}/incrementar`, { method: "POST" });
    const data = await res.json();
    setValor(data.valor);
  };

  return (
    <div style={{ textAlign: "center", marginTop: "3rem" }}>
      <h1>Contador conectado a FastAPI + PostgreSQL</h1>
      <p style={{ fontSize: "2rem" }}>{valor}</p>
      <button onClick={incrementar} style={{ fontSize: "1.2rem" }}>
        Incrementar
      </button>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
