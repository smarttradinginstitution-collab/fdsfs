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
    Supporta algoritmi sia RS256 che ES256.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)

        # Trova la chiave corretta dal JWKS basandosi sul 'kid' del token
        signing_key = None
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                signing_key = key
                break

        if not signing_key:
            raise HTTPException(status_code=401, detail="Chiave pubblica per la validazione del token non trovata.")

        # Costruisce la chiave pubblica. `jwk.construct` gestisce i diversi
        # formati di chiave (es. RSA vs EC) in base al 'kty'.
        public_key = jwk.construct(signing_key)

        # Decodifica il token, accettando gli algoritmi asimmetrici comuni di Supabase
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256", "ES256"],
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
