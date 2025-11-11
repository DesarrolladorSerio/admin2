-- Initialization script
CREATE TABLE IF NOT EXISTS contador (
    id SERIAL PRIMARY KEY,
    valor INT DEFAULT 0
);

INSERT INTO contador (id, valor)
VALUES (1, 0)
ON CONFLICT (id) DO NOTHING;
