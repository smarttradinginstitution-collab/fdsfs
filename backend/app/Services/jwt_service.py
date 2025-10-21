# app/Services/jwt_service.py
import httpx
from jose import jwt, jwk
from jose.exceptions import JWTError
from cachetools import TTLCache
from fastapi import HTTPException, status
from app.config import settings

# Cache per le chiavi JWKS con un TTL (Time To Live) di 1 ora
jwks_cache = TTLCache(maxsize=1, ttl=3600)

async def get_jwks():
    """
    Recupera le chiavi JWKS da Supabase, utilizzando una cache per evitare
    chiamate di rete ripetute.
    """
    if "jwks" in jwks_cache:
        return jwks_cache["jwks"]

    url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            jwks = response.json()
            jwks_cache["jwks"] = jwks
            return jwks
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Impossibile recuperare le chiavi di validazione JWT da Supabase: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore imprevisto durante il recupero delle chiavi JWKS: {e}",
        )

def validate_token_local(token: str, jwks: dict) -> dict:
    """
    Decodifica e valida un token JWT localmente utilizzando le chiavi JWKS fornite.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
        if not rsa_key:
            raise HTTPException(status_code=401, detail="Chiave pubblica per la validazione del token non trovata.")

        public_key = jwk.construct(rsa_key)

        # L'audience 'aud' di default è 'authenticated'.
        # L'issuer 'iss' deve corrispondere all'URL del tuo progetto Supabase.
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="authenticated",
            issuer=f"{settings.SUPABASE_URL}/auth/v1",
        )
        return payload

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token non valido o scaduto: {e}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante la validazione del token: {e}",
        )
