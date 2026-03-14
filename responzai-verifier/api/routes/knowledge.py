# api/routes/knowledge.py

import httpx
import re
from html.parser import HTMLParser
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from api.security import require_api_key

router = APIRouter()


class IngestRequest(BaseModel):
    url: str
    title: str
    source_type: str = "primary"  # primary, secondary, own


class IngestTextRequest(BaseModel):
    content: str
    title: str
    source_type: str = "primary"
    source_url: Optional[str] = ""


class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "nav", "header", "footer"):
            self.skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav", "header", "footer"):
            self.skip = False
        if tag in ("p", "div", "br", "li", "h1", "h2", "h3", "h4", "tr"):
            self.text_parts.append("\n\n")

    def handle_data(self, data):
        if not self.skip:
            self.text_parts.append(data.strip())

    def get_text(self) -> str:
        text = " ".join(self.text_parts)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        return text.strip()


@router.post("/knowledge/ingest")
async def ingest_from_url(body: IngestRequest, _: str = Depends(require_api_key)):
    """
    Laedt eine URL und nimmt den Text in die Wissensbasis auf.

    n8n ruft diesen Endpoint auf, wenn Pia (PULSE) eine neue
    EUR-Lex-Veroeffentlichung oder Gesetzesaenderung findet.

    Parameter:
    - url: Die URL des Dokuments (z.B. EUR-Lex-Link)
    - title: Titel der Quelle (z.B. "EU AI Act Amendment 2026")
    - source_type: "primary" (Gesetze), "secondary" (Richtlinien), "own" (eigene Inhalte)
    """
    try:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.get(body.url)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"URL konnte nicht geladen werden: {str(e)}")

    extractor = HTMLTextExtractor()
    extractor.feed(response.text)
    text = extractor.get_text()

    if len(text.strip()) < 100:
        raise HTTPException(status_code=422, detail="Extrahierter Text zu kurz (< 100 Zeichen). Pruefe die URL.")

    try:
        from database.seed import seed_database
        await seed_database(text, body.title, body.source_type, body.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Speichern: {str(e)}")

    return {
        "status": "ingested",
        "title": body.title,
        "source_type": body.source_type,
        "url": body.url,
        "text_length": len(text),
    }


@router.post("/knowledge/update")
async def update_from_url(body: IngestRequest, _: str = Depends(require_api_key)):
    """
    Aktualisiert eine bestehende Quelle in der Wissensbasis.

    Funktioniert wie /knowledge/ingest - seed_database() erkennt
    automatisch ob eine Quelle neu oder bereits vorhanden ist
    (Hash-Vergleich). Aendert sich der Text, werden die alten
    Chunks geloescht und neue gespeichert.
    """
    return await ingest_from_url(body, _)


@router.post("/knowledge/ingest-text")
async def ingest_raw_text(body: IngestTextRequest, _: str = Depends(require_api_key)):
    """
    Nimmt einen Text direkt (ohne URL) in die Wissensbasis auf.

    Fuer Faelle wo n8n den Text bereits extrahiert hat,
    z.B. aus einem Newsletter oder CMS-Inhalt.
    """
    if len(body.content.strip()) < 100:
        raise HTTPException(status_code=422, detail="Text zu kurz (< 100 Zeichen).")

    try:
        from database.seed import seed_database
        await seed_database(body.content, body.title, body.source_type, body.source_url or "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Speichern: {str(e)}")

    return {
        "status": "ingested",
        "title": body.title,
        "source_type": body.source_type,
        "text_length": len(body.content),
    }
