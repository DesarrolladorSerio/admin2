from enum import Enum
from functools import wraps
from typing import List

from db_auth import User
from fastapi import Depends, HTTPException, status


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    EMPLOYEE = "employee"

def require_role(allowed_roles: List[UserRole]):
    """Decorador para verificar que el usuario tenga el rol requerido."""
    def dependency(current_user: User):
        if not current_user.role or current_user.role not in [role.value for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes para realizar esta acción"
            )
        return current_user
    return dependency