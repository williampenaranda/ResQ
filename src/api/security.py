from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.security.components.servicioAutenticacion import verificar_token

bearer_scheme = HTTPBearer(auto_error=True)

async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """
    Lee el token del header Authorization: Bearer <token> y lo verifica.
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