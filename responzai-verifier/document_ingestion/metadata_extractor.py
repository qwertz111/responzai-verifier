# document_ingestion/metadata_extractor.py

import os
from datetime import datetime

def extract_metadata(file_path: str, mime_type: str) -> dict:
    """
    Liest Metadaten aus der Datei.

    Warum Metadaten?
    Pia braucht das Datum, um die Aktualität zu beurteilen.
    Simon nutzt den Dokumenttitel für den Kontext.
    Sven braucht den Autor, um Quellen zuzuordnen.
    """
    stat = os.stat(file_path)

    metadata = {
        "file_size_bytes": stat.st_size,
        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }

    # Dokumentspezifische Metadaten
    if mime_type == "application/pdf":
        metadata.update(_pdf_metadata(file_path))
    elif "wordprocessingml" in mime_type:
        metadata.update(_docx_metadata(file_path))

    return metadata


def _pdf_metadata(file_path: str) -> dict:
    import fitz
    doc = fitz.open(file_path)
    meta = doc.metadata
    doc.close()
    return {
        "title": meta.get("title", ""),
        "author": meta.get("author", ""),
        "subject": meta.get("subject", ""),
        "creator": meta.get("creator", ""),
        "creation_date": meta.get("creationDate", ""),
    }


def _docx_metadata(file_path: str) -> dict:
    from docx import Document
    doc = Document(file_path)
    props = doc.core_properties
    return {
        "title": props.title or "",
        "author": props.author or "",
        "subject": props.subject or "",
        "created": props.created.isoformat() if props.created else "",
        "modified": props.modified.isoformat() if props.modified else "",
    }
