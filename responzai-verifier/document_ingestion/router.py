# document_ingestion/router.py

import mimetypes
from pathlib import Path
from typing import Optional

from .parsers.pdf_parser import parse_pdf
from .parsers.docx_parser import parse_docx
from .parsers.xlsx_parser import parse_xlsx
from .parsers.pptx_parser import parse_pptx
from .parsers.odt_parser import parse_odt
from .parsers.html_parser import parse_html
from .parsers.markdown_parser import parse_markdown
from .parsers.txt_parser import parse_txt
from .parsers.email_parser import parse_email
from .parsers.image_parser import parse_image

# Zuordnung: MIME-Type oder Endung → Parser-Funktion
PARSERS = {
    "application/pdf": parse_pdf,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": parse_docx,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": parse_xlsx,
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": parse_pptx,
    "application/vnd.oasis.opendocument.text": parse_odt,
    "text/html": parse_html,
    "text/markdown": parse_markdown,
    "text/plain": parse_txt,
    "text/csv": parse_txt,
    "message/rfc822": parse_email,
    "image/png": parse_image,
    "image/jpeg": parse_image,
    "image/tiff": parse_image,
}

# Zusätzliche Zuordnung über Dateiendungen (als Fallback)
EXTENSION_MAP = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".odt": "application/vnd.oasis.opendocument.text",
    ".ods": "application/vnd.oasis.opendocument.spreadsheet",
    ".odp": "application/vnd.oasis.opendocument.presentation",
    ".html": "text/html",
    ".htm": "text/html",
    ".md": "text/markdown",
    ".txt": "text/plain",
    ".csv": "text/csv",
    ".eml": "message/rfc822",
    ".msg": "message/rfc822",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
}


def detect_format(filename: str, content_type: Optional[str] = None) -> str:
    """
    Erkennt das Format einer Datei.

    Zwei Wege:
    1. Der Browser schickt den Content-Type mit (zuverlässiger).
    2. Wir schauen auf die Dateiendung (Fallback).

    Warum beides?
    Manchmal schickt der Browser den falschen Content-Type.
    Manchmal hat die Datei eine ungewöhnliche Endung.
    Mit beiden Methoden zusammen erkennen wir fast alles.
    """
    if content_type and content_type in PARSERS:
        return content_type

    ext = Path(filename).suffix.lower()
    if ext in EXTENSION_MAP:
        return EXTENSION_MAP[ext]

    # Letzter Versuch: mimetypes-Bibliothek
    guessed, _ = mimetypes.guess_type(filename)
    if guessed and guessed in PARSERS:
        return guessed

    raise ValueError(
        f"Unbekanntes Dateiformat: {filename}. "
        f"Unterstützte Formate: {', '.join(EXTENSION_MAP.keys())}"
    )


async def ingest_document(
    file_path: str,
    filename: str,
    content_type: Optional[str] = None
) -> dict:
    """
    Hauptfunktion: Nimmt eine Datei entgegen und gibt
    strukturierten Text zurück.

    Ablauf:
    1. Format erkennen
    2. Richtigen Parser wählen
    3. Text extrahieren
    4. Text bereinigen und normalisieren
    5. Metadaten auslesen (Autor, Datum, Seitenzahl)

    Rückgabe:
    {
        "filename": "vertrag.pdf",
        "format": "application/pdf",
        "pages": 12,
        "text": "Der extrahierte Text...",
        "sections": [...],    # Text aufgeteilt nach Abschnitten
        "metadata": {...},    # Autor, Datum etc.
    }
    """
    from .preprocessor import clean_text
    from .metadata_extractor import extract_metadata

    mime_type = detect_format(filename, content_type)
    parser = PARSERS[mime_type]

    # Text extrahieren
    raw_result = await parser(file_path)

    # Text bereinigen
    cleaned_text = clean_text(raw_result["text"])

    # Metadaten auslesen
    metadata = extract_metadata(file_path, mime_type)

    return {
        "filename": filename,
        "format": mime_type,
        "pages": raw_result.get("pages", 1),
        "text": cleaned_text,
        "sections": raw_result.get("sections", []),
        "metadata": metadata,
        "raw_length": len(raw_result["text"]),
        "cleaned_length": len(cleaned_text),
    }
