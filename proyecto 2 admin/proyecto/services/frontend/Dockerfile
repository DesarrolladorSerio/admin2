# Imagen base específica (no latest)
FROM node:20.11.1-alpine3.19

WORKDIR /app

# Instalación de dependencias
COPY package.json package-lock.json* ./
RUN npm install

# Copia del código
COPY . .

# Exponer puerto de Vite
EXPOSE 5173

# Comando por defecto: modo dev con host abierto
CMD ["npm", "run", "dev", "--", "--host"]
