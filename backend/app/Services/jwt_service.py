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
    print("DEBUG_JWT: Entered get_jwks")
    if "jwks" in jwks_cache:
        print("DEBUG_JWT: Found JWKS in cache.")
        return jwks_cache["jwks"]

    print("DEBUG_JWT: JWKS not in cache. Fetching from Supabase.")
    url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    try:
        async with httpx.AsyncClient() as client:
            print(f"DEBUG_JWT: Making HTTP GET request to {url}")
            response = await client.get(url)
            print(f"DEBUG_JWT: Received response with status code {response.status_code}")
            response.raise_for_status()
            jwks = response.json()
            jwks_cache["jwks"] = jwks
            print("DEBUG_JWT: Successfully fetched and cached JWKS.")
            return jwks
    except httpx.HTTPStatusError as e:
        print(f"ERROR_JWT: HTTP error while fetching JWKS: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Impossibile recuperare le chiavi di validazione JWT da Supabase: {e}",
        )
    except Exception as e:
        print(f"ERROR_JWT: Unexpected error in get_jwks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore imprevisto durante il recupero delle chiavi JWKS: {e}",
        )

def validate_token_local(token: str, jwks: dict) -> dict:
    """
    Decodifica e valida un token JWT localmente utilizzando le chiavi JWKS fornite.
    """
    print("DEBUG_JWT: Entered validate_token_local")
    try:
        print("DEBUG_JWT: Step 1: Getting unverified header.")
        unverified_header = jwt.get_unverified_header(token)
        print(f"DEBUG_JWT: Step 1 successful. Header: {unverified_header}")

        rsa_key = {}
        print("DEBUG_JWT: Step 2: Searching for matching public key (kid).")
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"], "kid": key["kid"], "use": key["use"],
                    "n": key["n"], "e": key["e"],
                }
                break

        if not rsa_key:
            print("ERROR_JWT: Step 2 failed. Public key not found.")
            raise HTTPException(status_code=401, detail="Chiave pubblica per la validazione del token non trovata.")
        print("DEBUG_JWT: Step 2 successful. Found matching public key.")

        print("DEBUG_JWT: Step 3: Constructing public key object.")
        public_key = jwk.construct(rsa_key)
        print("DEBUG_JWT: Step 3 successful.")

        print("DEBUG_JWT: Step 4: Decoding token.")
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="authenticated",
            issuer=f"{settings.SUPABASE_URL}/auth/v1",
        )
        print("DEBUG_JWT: Step 4 successful. Token decoded.")
        return payload

    except JWTError as e:
        print(f"ERROR_JWT: JWTError during validation: {e}")
        raise HTTPException(status_code=401, detail=f"Token non valido o scaduto: {e}")
    except Exception as e:
        print(f"ERROR_JWT: Unexpected error in validate_token_local: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante la validazione del token: {e}",
        )
