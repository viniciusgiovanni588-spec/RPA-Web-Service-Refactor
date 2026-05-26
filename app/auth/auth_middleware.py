from fastapi import Request, HTTPException, status
import jwt
from jwt import PyJWKClient

from core.database import SUPABASE_URL,SUPABASE_JWKS_URL

"""
Cliente responsável por buscar as chaves públicas (JWKS)
usadas para validar assinaturas dos tokens JWT emitidos pelo Supabase.
"""
jwks_client = PyJWKClient(SUPABASE_URL+SUPABASE_JWKS_URL)

def get_current_user(request: Request):
    """
    Autentica o usuário com base no token JWT armazenado em cookie.

    Essa função valida o token usando a chave pública (JWKS) do provedor
    de autenticação (Supabase) e retorna o payload decodificado.

    Args:
        request (Request): Requisição HTTP do FastAPI contendo os cookies.
    Returns:
        dict: Payload decodificado do JWT contendo informações do usuário autenticado.
    Raises:
    HTTPException:
        - 401 Not authenticated: quando não existe token no cookie
        - 401 Token expired: quando o token JWT expirou
        - 401 Invalid token: quando o token é inválido ou não pode ser verificado
    """
    token = request.cookies.get('access_token')

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    try:

        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            options={"verify_aud": False}  # Desabilita a verificação de audiência
        )

        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")