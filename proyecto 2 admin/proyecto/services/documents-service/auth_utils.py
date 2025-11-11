"""
Utilidades de autenticación para el servicio de documentos.
Centraliza la lógica de autenticación JWT y comunicación con el servicio de autenticación.
"""

import logging
from typing import Any, Dict

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

# Configuración
SECRET_KEY = "un-secreto-muy-fuerte-y-largo"
ALGORITHM = "HS256"
AUTH_SERVICE_URL = "http://auth-service:8001"

# Configurar logging
logger = logging.getLogger(__name__)

# Configurar esquema de autenticación
security = HTTPBearer()

async def get_current_user(token: str = Depends(security)) -> Dict[str, Any]:
    """
    Obtiene el usuario actual desde el token JWT.
    Este método es idéntico al de otros servicios para mantener la consistencia.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extraer el token del objeto credentials
        token_str = token.credentials if hasattr(token, 'credentials') else str(token)
            
        # Decodificar el token JWT
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        email: str = payload.get("sub")
        role: str = payload.get("role", "user")
        
        if user_id is None or email is None:
            logger.warning("Token inválido: falta user_id o email")
            raise credentials_exception
            
        # Opcional: Verificar que el usuario realmente existe en el servicio de auth.
        # Esto añade una capa de seguridad pero también latencia.
        # Por ahora, confiamos en el token si es válido.
        
        return {
            "id": user_id,
            "email": email,
            "role": role,
        }
        
    except JWTError as e:
        logger.warning(f"Error JWT: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Error inesperado en autenticación: {e}")
        raise credentials_exception