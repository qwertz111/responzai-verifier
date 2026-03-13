"""
Tests fuer die Document Ingestion Pipeline.

Prueft Format-Erkennung (detect_format), Text-Bereinigung (clean_text),
und den sicheren Datei-Upload (save_upload).
Keine echten Dateien oder Datenbank-Verbindungen nötig.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, AsyncMock

# Fixtures laden
FIXTURES_PATH = Path(__file__).parent / "fixtures.json"
with open(FIXTURES_PATH, encoding="utf-8") as f:
    FIXTURES = json.load(f)


# ─── detect_format Tests ─────────────────────────────────────────────────────

def test_detect_format_pdf():
    """detect_format('test.pdf') muss 'application/pdf' zurueckgeben."""
    from document_ingestion.router import detect_format

    result = detect_format("test.pdf")
    assert result == "application/pdf", f"Erwartet 'application/pdf', bekam: {result}"


def test_detect_format_docx():
    """detect_format('test.docx') muss den korrekten MIME-Typ zurueckgeben."""
    from document_ingestion.router import detect_format

    expected = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    result = detect_format("test.docx")
    assert result == expected, f"Erwartet '{expected}', bekam: {result}"


def test_detect_format_xlsx():
    """detect_format('test.xlsx') muss den korrekten MIME-Typ zurueckgeben."""
    from document_ingestion.router import detect_format

    expected = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    result = detect_format("test.xlsx")
    assert result == expected


def test_detect_format_unknown():
    """detect_format('test.xyz') muss eine ValueError-Exception werfen."""
    from document_ingestion.router import detect_format

    with pytest.raises(ValueError, match="Unbekanntes Dateiformat"):
        detect_format("dokument.xyz")


def test_detect_format_with_content_type():
    """detect_format soll content_type bevorzugen, wenn angegeben."""
    from document_ingestion.router import detect_format

    # Dateiendung wäre .txt, aber Content-Type ist application/pdf
    result = detect_format("upload.bin", content_type="application/pdf")
    assert result == "application/pdf"


# ─── clean_text Tests ─────────────────────────────────────────────────────────

def test_clean_text_removes_control_chars():
    """clean_text muss unsichtbare Steuerzeichen entfernen."""
    from document_ingestion.preprocessor import clean_text

    # Steuerzeichen einbetten (BEL, BS, VT, FF etc.)
    dirty = "Normaler Text\x07mit\x08Steuerzeichen\x0c."
    result = clean_text(dirty)

    # Keine Steuerzeichen mehr im Ergebnis (ausser \n und \t)
    for char in result:
        code = ord(char)
        assert code >= 0x20 or char in ("\n", "\t"), (
            f"Steuerzeichen U+{code:04X} sollte entfernt worden sein"
        )


def test_clean_text_joins_hyphenation():
    """'Verant-\\nwortung' soll zu 'Verantwortung' zusammengefuehrt werden."""
    from document_ingestion.preprocessor import clean_text

    # Typischer PDF-Umbruch-Bindestrich
    dirty = "Verant-\nwortung fuer KI-\nSysteme."
    result = clean_text(dirty)

    assert "Verantwortung" in result, f"'Verantwortung' erwartet, Ergebnis: {result}"
    assert "Verant-" not in result, "Bindestrich-Trennung sollte aufgeloest sein"


def test_clean_text_collapses_multiple_spaces():
    """Mehrfache Leerzeichen sollen zu einem Leerzeichen zusammengefuehrt werden."""
    from document_ingestion.preprocessor import clean_text

    dirty = "KI-Kompetenz   ist   wichtig."
    result = clean_text(dirty)

    assert "  " not in result, "Doppelte Leerzeichen sollten entfernt sein"


def test_clean_text_preserves_content():
    """clean_text darf den eigentlichen Inhalt nicht veraendern."""
    from document_ingestion.preprocessor import clean_text

    text = FIXTURES["sample_text"]
    result = clean_text(text)

    # Schluesselwoerter muessen erhalten bleiben
    assert "EU AI Act" in result
    assert "Artikel 4" in result or "responzai" in result


# ─── save_upload Tests ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_save_upload_rejects_exe():
    """save_upload soll .exe-Dateien ablehnen (ValueError)."""
    from document_ingestion.storage import save_upload

    fake_content = b"MZ" + b"\x00" * 100  # EXE-Header-Anfang

    with pytest.raises(ValueError, match="nicht erlaubt"):
        await save_upload(fake_content, "malware.exe")


@pytest.mark.asyncio
async def test_save_upload_rejects_large_file():
    """save_upload soll Dateien groesser als 50 MB ablehnen (ValueError)."""
    from document_ingestion.storage import save_upload

    # 51 MB - ueberschreitet das Limit
    oversized_content = b"x" * (51 * 1024 * 1024)

    with pytest.raises(ValueError, match="zu groß"):
        await save_upload(oversized_content, "grossedatei.pdf")


@pytest.mark.asyncio
async def test_save_upload_valid_pdf():
    """save_upload soll eine gueltige PDF-Datei akzeptieren und Metadaten zurueckgeben."""
    from document_ingestion.storage import save_upload

    fake_pdf = b"%PDF-1.4 kleines Test-Dokument"

    # Verzeichnis-Erstellung und Datei-Schreiben mocken
    with patch("document_ingestion.storage.UPLOAD_DIR") as mock_dir, \
         patch("builtins.open", mock_open()) as mock_file:

        mock_dir.__truediv__ = MagicMock(return_value=Path("/tmp/test.pdf"))
        mock_dir.mkdir = MagicMock()

        result = await save_upload(fake_pdf, "test.pdf")

    assert "stored_path" in result, "Ergebnis muss 'stored_path' enthalten"
    assert "hash" in result, "Ergebnis muss 'hash' enthalten"
    assert "size" in result, "Ergebnis muss 'size' enthalten"
    assert result["original_name"] == "test.pdf"


def test_allowed_extensions():
    """ALLOWED_EXTENSIONS muss alle erwarteten Dateitypen enthalten."""
    from document_ingestion.storage import ALLOWED_EXTENSIONS

    # Pflichtformate gemaess Spezifikation
    required = {".pdf", ".docx", ".xlsx", ".pptx", ".odt", ".html", ".md", ".txt",
                ".csv", ".eml", ".png", ".jpg", ".jpeg", ".tiff"}

    missing = required - ALLOWED_EXTENSIONS
    assert not missing, f"Fehlende Erweiterungen in ALLOWED_EXTENSIONS: {missing}"

    # Gefaehrliche Typen duerfen NICHT erlaubt sein
    dangerous = {".exe", ".sh", ".py", ".bat", ".cmd", ".ps1"}
    forbidden_present = dangerous & ALLOWED_EXTENSIONS
    assert not forbidden_present, (
        f"Gefaehrliche Erweiterungen in ALLOWED_EXTENSIONS gefunden: {forbidden_present}"
    )
