# api/security.py
# Rate Limiting und API Key Auth

import os
from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate Limiter: zaehlt Requests pro IP-Adresse
limiter = Limiter(key_func=get_remote_address)

# API Key Header: "X-API-Key: <key>"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Prueft ob ein gueltiger API-Key im Header mitgeschickt wurde.

    Wie benutzen:
    Header setzen: X-API-Key: <dein-key>

    Kein Key konfiguriert (API_KEY nicht in .env)?
    Dann wird Auth uebersprungen (nuetzlich fuer lokale Entwicklung).
    """
    expected_key = os.environ.get("API_KEY", "")

    # Kein Key konfiguriert = Auth deaktiviert (Entwicklungsmodus)
    if not expected_key:
        return "dev-mode"

    if not api_key or api_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail="Ungültiger oder fehlender API-Key. Header: X-API-Key: <key>",
        )

    return api_key
