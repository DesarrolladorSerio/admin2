"""
Utilidades de autenticación para el servicio de reservas.
Centraliza la lógica de autenticación JWT y comunicación con el servicio de autenticación.
"""

import logging
from typing import Any, Dict, Optional

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
    
    Args:
        token: Token JWT desde el header Authorization
        
    Returns:
        Dict con información del usuario (id, email, role, etc.)
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extraer el token del objeto credentials
        if hasattr(token, 'credentials'):
            token_str = token.credentials
        else:
            token_str = str(token)
            
        # Decodificar el token JWT
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        email: str = payload.get("sub")  # 'sub' contiene el email
        role: str = payload.get("role", "user")
        
        if user_id is None or email is None:
            logger.warning("Token inválido: missing user_id or email")
            raise credentials_exception
            
        # Verificar que el usuario existe en el servicio de autenticación
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{AUTH_SERVICE_URL}/api/auth/verify-user/{user_id}",
                    headers={"Authorization": f"Bearer {token_str}"}
                )
                
                if response.status_code != 200:
                    logger.warning(f"Usuario {user_id} no encontrado en auth service")
                    raise credentials_exception
                    
                user_data = response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Error conectando con auth service: {e}")
            # En caso de error de conexión, usar datos del token
            user_data = {
                "id": user_id,
                "email": email,
                "role": role,
                "is_active": True
            }
        
        # Verificar que el usuario está activo
        if not user_data.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled"
            )
        
        return {
            "id": user_data.get("id", user_id),
            "email": user_data.get("email", email),
            "role": user_data.get("role", role),
            "is_active": user_data.get("is_active", True),
            "name": user_data.get("name", ""),
        }
        
    except JWTError as e:
        logger.warning(f"Error JWT: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Error inesperado en autenticación: {e}")
        raise credentials_exception

def require_role(required_role: str):
    """
    Decorador para requerir un rol específico.
    
    Args:
        required_role: Rol requerido ('admin', 'employee', 'user')
        
    Returns:
        Función que valida el rol del usuario
    """
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if current_user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return current_user
    
    return role_checker

def require_admin():
    """Shortcut para requerir rol de administrador."""
    return require_role("admin")

def require_employee():
    """Shortcut para requerir rol de empleado o superior."""
    async def employee_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role", "user")
        if user_role not in ["admin", "employee"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Employee or admin role required"
            )
        return current_user
    
    return employee_checker

async def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica un token JWT sin lanzar excepciones.
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        Dict con datos del usuario si es válido, None si es inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        email: str = payload.get("sub")
        role: str = payload.get("role", "user")
        
        if user_id is None or email is None:
            return None
            
        return {
            "id": user_id,
            "email": email,
            "role": role
        }
        
    except JWTError:
        return None
    except Exception:
        return None