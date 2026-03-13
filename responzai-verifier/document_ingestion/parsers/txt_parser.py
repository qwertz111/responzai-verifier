# document_ingestion/parsers/txt_parser.py


async def parse_txt(file_path: str) -> dict:
    """
    Liest einfache Text- und CSV-Dateien ein.

    Warum zwei Encodings?
    Viele ältere Dokumente, besonders aus deutschen Behörden oder Legacy-Systemen,
    sind noch in Latin-1 (ISO-8859-1) kodiert, nicht in UTF-8. Wir versuchen
    zuerst UTF-8, das ist der moderne Standard. Falls das scheitert, fallen wir
    auf Latin-1 zurück, das fast alle europäischen Zeichen abdeckt.

    CSV-Dateien werden wie normaler Text behandelt. Strukturierte Auswertung
    übernimmt der xlsx_parser, wenn nötig.
    """
    text = _read_with_fallback(file_path)

    return {
        "text": text,
        "pages": 1,
        "sections": [
            {
                "heading": "Text",
                "text": text,
            }
        ],
    }


def _read_with_fallback(file_path: str) -> str:
    """
    Liest eine Datei mit UTF-8, fällt bei Fehler auf Latin-1 zurück.

    Latin-1 ist immer erfolgreich, weil jedes Byte ein gültiges Zeichen ist.
    Es dient damit als sicherer letzter Ausweg.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read()
