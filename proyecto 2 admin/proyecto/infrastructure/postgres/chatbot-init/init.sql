-- Script de inicialización para la base de datos del ChatBot
-- PostgreSQL 16.4

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de usuarios (referencia simplificada)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- Tabla de sesiones de chat (soporta sesiones anónimas con user_id NULL)
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,  -- Nullable para sesiones anónimas
    session_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX idx_chat_sessions_is_active ON chat_sessions(is_active);
CREATE INDEX idx_chat_sessions_anonymous ON chat_sessions(session_id) WHERE user_id IS NULL;

-- Tabla de mensajes de chat
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER,
    response_time_ms INTEGER,
    CONSTRAINT fk_chat_messages_session FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_timestamp ON chat_messages(timestamp);
CREATE INDEX idx_chat_messages_role ON chat_messages(role);

-- Tabla de métricas de uso (soporta métricas de sesiones anónimas)
CREATE TABLE IF NOT EXISTS chat_metrics (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,  -- Nullable para sesiones anónimas
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_messages INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    avg_response_time_ms FLOAT DEFAULT 0.0,
    topics_discussed TEXT DEFAULT '',
    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5)
);

CREATE INDEX idx_chat_metrics_user_id ON chat_metrics(user_id);
CREATE INDEX idx_chat_metrics_date ON chat_metrics(date);
CREATE INDEX idx_chat_metrics_session_id ON chat_metrics(session_id);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar updated_at en chat_sessions
CREATE TRIGGER update_chat_sessions_updated_at
    BEFORE UPDATE ON chat_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Vista para estadísticas agregadas por usuario
CREATE OR REPLACE VIEW user_chat_stats AS
SELECT 
    u.id as user_id,
    u.email,
    u.nombre,
    COUNT(DISTINCT cs.id) as total_sessions,
    COUNT(cm.id) as total_messages,
    COALESCE(SUM(cme.total_tokens), 0) as total_tokens_used,
    COALESCE(AVG(cme.avg_response_time_ms), 0) as avg_response_time,
    MAX(cs.updated_at) as last_interaction
FROM users u
LEFT JOIN chat_sessions cs ON u.id = cs.user_id
LEFT JOIN chat_messages cm ON cs.id = cm.session_id
LEFT JOIN chat_metrics cme ON u.id = cme.user_id
GROUP BY u.id, u.email, u.nombre;

-- Vista para métricas diarias del sistema
CREATE OR REPLACE VIEW daily_chatbot_metrics AS
SELECT 
    DATE(date) as metric_date,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT session_id) as total_sessions,
    SUM(total_messages) as total_messages,
    SUM(total_tokens) as total_tokens,
    AVG(avg_response_time_ms) as avg_response_time,
    AVG(satisfaction_rating) as avg_satisfaction
FROM chat_metrics
GROUP BY DATE(date)
ORDER BY metric_date DESC;

-- Comentarios en las tablas para documentación
COMMENT ON TABLE users IS 'Referencia simplificada de usuarios del sistema';
COMMENT ON TABLE chat_sessions IS 'Sesiones de conversación del chatbot con usuarios';
COMMENT ON TABLE chat_messages IS 'Mensajes individuales en las conversaciones del chatbot';
COMMENT ON TABLE chat_metrics IS 'Métricas de uso y rendimiento del chatbot';
COMMENT ON VIEW user_chat_stats IS 'Estadísticas agregadas de uso del chatbot por usuario';
COMMENT ON VIEW daily_chatbot_metrics IS 'Métricas diarias agregadas del sistema de chatbot';

-- Grants para el usuario de la aplicación
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO admin;

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'Base de datos del ChatBot inicializada correctamente';
    RAISE NOTICE 'Tablas creadas: users, chat_sessions, chat_messages, chat_metrics';
    RAISE NOTICE 'Vistas creadas: user_chat_stats, daily_chatbot_metrics';
END $$;
