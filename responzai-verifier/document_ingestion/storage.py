# document_ingestion/storage.py

import os
import uuid
import hashlib
from pathlib import Path

UPLOAD_DIR = Path("/app/data/uploads")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Erlaubte Dateitypen (Sicherheit: keine ausführbaren Dateien)
ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".xlsx", ".pptx",
    ".odt", ".ods", ".odp",
    ".html", ".htm", ".md", ".txt", ".csv",
    ".eml", ".msg",
    ".png", ".jpg", ".jpeg", ".tiff", ".tif",
}


async def save_upload(file_content: bytes, filename: str) -> dict:
    """
    Speichert eine hochgeladene Datei sicher auf dem Server.

    Sicherheitsmaßnahmen:
    1. Nur erlaubte Dateitypen (keine .exe, .sh, .py etc.)
    2. Maximale Dateigröße: 50 MB
    3. Dateiname wird durch eine UUID ersetzt (verhindert
       Path-Traversal-Angriffe wie "../../etc/passwd")
    4. Dateien werden in einem eigenen Verzeichnis gespeichert
    5. Hash wird berechnet, um Duplikate zu erkennen
    """
    # Dateityp prüfen
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Dateityp '{ext}' nicht erlaubt. "
            f"Erlaubt: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Dateigröße prüfen
    if len(file_content) > MAX_FILE_SIZE:
        raise ValueError(
            f"Datei zu groß: {len(file_content)} Bytes. "
            f"Maximum: {MAX_FILE_SIZE} Bytes (50 MB)."
        )

    # Hash berechnen (für Duplikat-Erkennung)
    file_hash = hashlib.sha256(file_content).hexdigest()

    # Sicheren Dateinamen generieren
    safe_name = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / safe_name

    # Verzeichnis erstellen, falls nicht vorhanden
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Datei speichern
    with open(file_path, "wb") as f:
        f.write(file_content)

    return {
        "stored_path": str(file_path),
        "original_name": filename,
        "hash": file_hash,
        "size": len(file_content),
    }
