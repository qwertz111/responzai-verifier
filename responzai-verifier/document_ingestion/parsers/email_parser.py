# document_ingestion/parsers/email_parser.py

import email
from email import policy
from email.parser import BytesParser


async def parse_email(file_path: str) -> dict:
    """
    Extrahiert Inhalt und Metadaten aus .eml-E-Mail-Dateien.

    E-Mails können relevante Aussagen zu KI-Produkten oder rechtlichen Themen
    enthalten, zum Beispiel Anfragen, offizielle Mitteilungen oder Berichte.
    Diese Funktion macht sie für die Agenten-Pipeline zugänglich.

    Vorgehen:
    1. E-Mail-Datei einlesen und parsen (Python-Standardbibliothek)
    2. Bevorzugt den Nur-Text-Body (text/plain)
    3. Falls nur HTML verfügbar, wird der Text per BeautifulSoup extrahiert
    4. Metadaten (Absender, Empfänger, Datum, Betreff) separat speichern

    Warum text/plain bevorzugen?
    HTML-E-Mails enthalten viel Formatierungs-Rauschen (Farben, Schriften, Layout).
    Der Nur-Text-Body enthält denselben inhaltlichen Text ohne dieses Rauschen.
    """
    with open(file_path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    subject = str(msg.get("subject", ""))
    sender = str(msg.get("from", ""))
    recipient = str(msg.get("to", ""))
    date = str(msg.get("date", ""))

    body = _extract_body(msg)

    heading = f"Betreff: {subject}" if subject else "E-Mail"
    full_text = f"{heading}\n\n{body}".strip()

    return {
        "text": full_text,
        "pages": 1,
        "sections": [
            {
                "heading": heading,
                "text": body,
            }
        ],
        "metadata": {
            "from": sender,
            "to": recipient,
            "date": date,
            "subject": subject,
        },
    }


def _extract_body(msg) -> str:
    """
    Extrahiert den Textkörper aus einer E-Mail.

    Reihenfolge der Präferenz:
    1. text/plain-Teil (direkt lesbar, kein Rauschen)
    2. text/html-Teil, gefiltert durch BeautifulSoup
    3. Leerer String, wenn kein Body gefunden wurde
    """
    plain_body = None
    html_body = None

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("content-disposition", ""))
            if "attachment" in disposition:
                continue
            if content_type == "text/plain" and plain_body is None:
                plain_body = _decode_part(part)
            elif content_type == "text/html" and html_body is None:
                html_body = _decode_part(part)
    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            plain_body = _decode_part(msg)
        elif content_type == "text/html":
            html_body = _decode_part(msg)

    if plain_body:
        return plain_body.strip()

    if html_body:
        return _strip_html(html_body).strip()

    return ""


def _decode_part(part) -> str:
    """
    Dekodiert einen E-Mail-Teil zu einem Python-String.

    E-Mail-Teile können verschiedene Zeichenkodierungen haben.
    Wir verlassen uns auf die policy=default-Einstellung, die
    moderne E-Mails korrekt behandelt, und fallen bei älteren
    Nachrichten auf UTF-8 zurück.
    """
    try:
        payload = part.get_payload(decode=True)
        charset = part.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="replace")
    except Exception:
        return ""


def _strip_html(html: str) -> str:
    """
    Entfernt HTML-Tags aus einem String mit BeautifulSoup.

    Wird nur verwendet, wenn kein Nur-Text-Body verfügbar ist.
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    return soup.get_text(separator="\n")
