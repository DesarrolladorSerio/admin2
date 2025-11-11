"""
Utilidades de autenticación compartidas para todos los servicios
Principio de DRY (Don't Repeat Yourself) y Responsabilidad Única
"""
import logging
from typing import Dict, Optional

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

# Configuración del esquema de seguridad
security = HTTPBearer()

class AuthService:
    """
    Servicio de autenticación centralizado
    Principio de Responsabilidad Única: Solo se encarga de verificar autenticación
    """
    
    def __init__(self, auth_service_url: str = "http://auth-service:8001"):
        self.auth_service_url = auth_service_url
        self.timeout = 10.0
    
    async def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verifica un token JWT contra el servicio de autenticación
        Principio de Inversión de Dependencias: Depende de una abstracción (HTTP API)
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.auth_service_url}/users/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "id": user_data.get("id"),
                        "email": user_data.get("email"),
                        "username": user_data.get("username"),  # Compatibilidad
                        "nombre": user_data.get("nombre"),
                        "rut": user_data.get("rut"),
                        "role": user_data.get("role", "user")  # Campo actualizado
                    }
                else:
                    logger.warning(f"Token verification failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error verificando token: {str(e)}")
            return None
    
    async def require_authentication(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict:
        """
        Middleware de autenticación que requiere un token válido
        """
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acceso requerido",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user_data = await self.verify_token(credentials.credentials)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user_data
    
    async def require_admin(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict:
        """
        Middleware que requiere permisos de administrador
        Principio de Segregación de Interfaces: Interfaz específica para admins
        """
        user_data = await self.require_authentication(credentials)
        
        if user_data.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos de administrador requeridos"
            )
        
        return user_data
    
    async def require_employee_or_admin(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict:
        """
        Middleware que requiere ser empleado o administrador
        """
        user_data = await self.require_authentication(credentials)
        
        allowed_roles = ["admin", "employee"]
        if user_data.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos de empleado o administrador requeridos"
            )
        
        return user_data

# Instancia global del servicio de autenticación
auth_service = AuthService()

# Funciones de conveniencia para usar como dependencias
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """Obtiene el usuario actual autenticado"""
    return await auth_service.require_authentication(credentials)

async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """Obtiene el usuario actual (debe ser admin)"""
    return await auth_service.require_admin(credentials)

async def get_current_employee_or_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """Obtiene el usuario actual (debe ser empleado o admin)"""
    return await auth_service.require_employee_or_admin(credentials)