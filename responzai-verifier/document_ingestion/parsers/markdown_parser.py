# document_ingestion/parsers/markdown_parser.py

import re


async def parse_markdown(file_path: str) -> dict:
    """
    Extrahiert Text aus Markdown-Dateien und teilt ihn in Sektionen auf.

    Markdown ist das Standardformat für technische Dokumentation und
    viele Wissensdatenbanken. Die Überschriften (# bis ######) sind
    natürliche Sektionsgrenzen.

    Warum kein Markdown-zu-HTML-Konverter?
    Für die reine Textextraktion ist ein Konverter überdimensioniert.
    Wir brauchen den Rohtext, keine gerenderte Darstellung. Eine einfache
    Zeilenanalyse reicht vollständig aus.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            content = f.read()

    sections = _split_by_headings(content)
    full_text = content

    return {
        "text": full_text,
        "pages": 1,
        "sections": sections,
    }


def _split_by_headings(content: str) -> list:
    """
    Zerlegt Markdown-Inhalt anhand von Überschriften in Sektionen.

    Eine Überschrift beginnt mit einem oder mehreren #-Zeichen,
    gefolgt von einem Leerzeichen. Alles darunter bis zur nächsten
    Überschrift gehört zu dieser Sektion.
    """
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    sections = []
    lines = content.splitlines(keepends=True)
    current_heading = ""
    current_lines = []

    for line in lines:
        match = heading_pattern.match(line.rstrip())
        if match:
            # Vorherige Sektion abschließen
            body = "".join(current_lines).strip()
            if body or current_heading:
                sections.append({"heading": current_heading, "text": body})
            current_heading = match.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Letzte Sektion speichern
    body = "".join(current_lines).strip()
    if body or current_heading:
        sections.append({"heading": current_heading, "text": body})

    # Fallback: keine Überschriften gefunden
    if not sections:
        sections = [{"heading": "", "text": content.strip()}]

    return sections
