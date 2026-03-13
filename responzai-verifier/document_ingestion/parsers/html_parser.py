# document_ingestion/parsers/html_parser.py

from bs4 import BeautifulSoup


# Tags, die keinen inhaltlichen Text enthalten und entfernt werden sollen
_TAGS_TO_REMOVE = ["script", "style", "nav", "footer", "head", "noscript", "iframe"]


async def parse_html(file_path: str) -> dict:
    """
    Extrahiert Text aus lokal gespeicherten HTML-Dateien.

    Diese Funktion ist für archivierte oder heruntergeladene HTML-Dateien gedacht,
    nicht für Web-Crawling. Web-Crawling übernimmt Pia (PULSE) mit eigenen Werkzeugen.

    Vorgehen:
    1. HTML einlesen und parsen (mit lxml als schnellem Parser)
    2. Nicht-inhaltliche Tags entfernen (Skripte, Navigation, Fußzeile usw.)
    3. Überschriften als Sektionsgrenzen verwenden
    4. Bereinigten Volltext und Sektionsliste zurückgeben

    Warum Sektionen über Überschriften?
    Überschriften strukturieren den Inhalt. Simon (SCOUT) kann so erkennen,
    in welchem Abschnitt einer Seite eine Behauptung steht.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_html = f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            raw_html = f.read()

    soup = BeautifulSoup(raw_html, "lxml")

    # Nicht-inhaltliche Tags entfernen
    for tag_name in _TAGS_TO_REMOVE:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    sections = _extract_sections(soup)
    full_text = "\n\n".join(
        f"{s['heading']}\n{s['text']}" if s["heading"] else s["text"]
        for s in sections
    ).strip()

    return {
        "text": full_text,
        "pages": 1,
        "sections": sections,
    }


def _extract_sections(soup: BeautifulSoup) -> list:
    """
    Teilt den HTML-Inhalt anhand von Überschriften in Sektionen auf.

    Jede Überschrift (h1-h6) beginnt eine neue Sektion. Der Text vor der
    ersten Überschrift wird als anonyme Einleitung gespeichert.
    """
    HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
    sections = []
    current_heading = ""
    current_texts = []

    body = soup.body or soup

    for element in body.descendants:
        # Nur direkte Text-Elemente und Überschriften interessieren uns
        if element.name in HEADING_TAGS:
            heading_text = element.get_text(separator=" ", strip=True)
            # Vorherige Sektion abschließen
            if current_texts:
                combined = " ".join(current_texts).strip()
                if combined:
                    sections.append({"heading": current_heading, "text": combined})
            current_heading = heading_text
            current_texts = []
        elif element.name in {"p", "li", "td", "th", "blockquote", "pre"}:
            text = element.get_text(separator=" ", strip=True)
            if text:
                current_texts.append(text)

    # Letzte Sektion speichern
    if current_texts:
        combined = " ".join(current_texts).strip()
        if combined:
            sections.append({"heading": current_heading, "text": combined})

    # Fallback: kein strukturierter Inhalt gefunden
    if not sections:
        plain = (soup.body or soup).get_text(separator="\n", strip=True)
        sections = [{"heading": "", "text": plain}]

    return sections
