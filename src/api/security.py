from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Union
from src.security.components.servicioAutenticacion import verificar_token
from src.security.entities.Usuario import TipoUsuario

bearer_scheme = HTTPBearer(auto_error=True)


async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """
    Lee el token del header Authorization: Bearer <token> y lo verifica.
    Retorna el payload del token que incluye el tipoUsuario del usuario.
    """
    token = credentials.credentials
    payload = verificar_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


def require_role(allowed_roles: Union[TipoUsuario, List[TipoUsuario]]):
    """
    Dependencia de FastAPI que verifica que el usuario tenga uno de los tipos de usuario permitidos.
    
    Args:
        allowed_roles: Un tipo de usuario único o una lista de tipos permitidos
    
    Returns:
        Una función de dependencia que verifica el tipoUsuario del usuario
    
    Example:
        @router.get("/admin-only")
        async def admin_endpoint(payload: dict = Depends(require_role(TipoUsuario.ADMINISTRADOR))):
            return {"message": "Solo administradores pueden ver esto"}
        
        @router.get("/operadores")
        async def operadores_endpoint(
            payload: dict = Depends(require_role([TipoUsuario.OPERADOR_EMERGENCIA, TipoUsuario.OPERADOR_AMBULANCIA]))
        ):
            return {"message": "Operadores pueden ver esto"}
    """
    # Normalizar a lista si es un solo tipo
    if isinstance(allowed_roles, TipoUsuario):
        allowed_roles = [allowed_roles]
    
    # Convertir tipos a valores string para comparación
    allowed_role_values = {tipo.value for tipo in allowed_roles}
    
    async def role_checker(payload: dict = Depends(require_auth)) -> dict:
        """
        Verifica que el usuario tenga uno de los tipos de usuario permitidos.
        """
        # Obtener el tipoUsuario del payload
        tipo_usuario_value = payload.get("tipoUsuario")
        
        if not tipo_usuario_value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario sin tipoUsuario asignado"
            )
        
        # Normalizar a string para comparación
        tipo_usuario_str = tipo_usuario_value.upper() if isinstance(tipo_usuario_value, str) else str(tipo_usuario_value).upper()
        
        # Verificar si el tipoUsuario del usuario está en los permitidos
        if tipo_usuario_str not in allowed_role_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere uno de los siguientes tipos de usuario: {[t.value for t in allowed_roles]}"
            )
        
        return payload
    
    return role_checker