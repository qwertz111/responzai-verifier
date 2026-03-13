# document_ingestion/parsers/odt_parser.py

from odf.opendocument import load
from odf import text as odf_text, teletype


async def parse_odt(file_path: str) -> dict:
    """
    Extrahiert Text aus OpenDocument-Textdateien (.odt).

    ODT ist das offene Standardformat von LibreOffice und OpenOffice.
    Viele öffentliche Stellen und Behörden in der EU verwenden es.
    Die odfpy-Bibliothek liest das Format direkt ohne externe Abhängigkeiten.

    Vorgehen:
    1. Dokument laden
    2. Alle Textabsätze der Reihe nach auslesen
    3. Text zu einem einzigen Block zusammenfassen

    Warum keine Sektionserkennung wie bei DOCX?
    ODT-Dateien haben zwar Überschriften-Stile, aber odfpy macht deren
    Erkennung aufwändiger. Da ODT-Dateien in der Praxis selten komplex
    strukturiert sind, genügt ein einfacher Textblock als eine Sektion.
    Falls nötig, kann die Erkennung später ergänzt werden.
    """
    doc = load(file_path)

    paragraphs = []
    for paragraph in doc.getElementsByType(odf_text.P):
        text = teletype.extractText(paragraph)
        if text.strip():
            paragraphs.append(text)

    full_text = "\n\n".join(paragraphs)

    return {
        "text": full_text,
        "pages": 1,
        "sections": [
            {
                "heading": "Dokument",
                "text": full_text,
            }
        ],
    }
