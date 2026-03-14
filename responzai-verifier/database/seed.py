# database/seed.py

"""
Wissensbasis-Erstbefuellung mit EU AI Act Text.

Verwendung:
    python -m database.seed                    # EU AI Act von EUR-Lex laden
    python -m database.seed --file path.txt    # Lokale Textdatei laden
"""

import argparse
import asyncio
import hashlib
import json
import sys

import httpx

from database.connection import get_connection
from processing.chunking import chunk_legal_text
from processing.embedding import create_embeddings


# EUR-Lex: EU AI Act (Regulation 2024/1689) - HTML version
EUR_LEX_URL = (
    "https://eur-lex.europa.eu/legal-content/DE/TXT/"
    "?uri=CELEX:32024R1689"
)


async def fetch_eu_ai_act() -> str:
    """Laedt den EU AI Act von EUR-Lex als Text."""
    print("Lade EU AI Act von EUR-Lex...")
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        response = await client.get(EUR_LEX_URL)
        response.raise_for_status()

    # HTML zu Text konvertieren (einfache Variante)
    from html.parser import HTMLParser

    class TextExtractor(HTMLParser):
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

    extractor = TextExtractor()
    extractor.feed(response.text)
    text = " ".join(extractor.text_parts)

    # Mehrfache Leerzeilen bereinigen
    import re
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)

    print(f"EU AI Act geladen: {len(text)} Zeichen, ~{len(text.split())} Woerter")
    return text


async def load_from_file(filepath: str) -> str:
    """Laedt Text aus einer lokalen Datei."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    print(f"Datei geladen: {filepath} ({len(text)} Zeichen)")
    return text


async def seed_database(text: str, source_title: str = "EU AI Act",
                         source_type: str = "primary",
                         source_url: str = "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024R1689"):
    """
    Befuellt die Wissensbasis mit dem gegebenen Text.

    Schritte:
    1. Quelle registrieren (oder bestehende aktualisieren)
    2. Text in Chunks zerlegen
    3. Embeddings erzeugen (Voyage-3, in Batches)
    4. Chunks + Embeddings in DB speichern
    """
    text_hash = hashlib.sha256(text.encode()).hexdigest()

    async with get_connection() as conn:
        # Pruefen ob Quelle bereits existiert
        existing = await conn.fetchrow(
            "SELECT id, hash FROM sources WHERE title = $1", source_title
        )

        if existing and existing["hash"] == text_hash:
            print(f"Quelle '{source_title}' ist bereits aktuell. Keine Aenderung noetig.")
            return

        if existing:
            # Quelle existiert, aber Text hat sich geaendert -> alte Chunks loeschen
            source_id = existing["id"]
            deleted = await conn.execute(
                "DELETE FROM chunks WHERE source_id = $1", source_id
            )
            await conn.execute(
                "UPDATE sources SET hash = $1, fetched_at = NOW() WHERE id = $2",
                text_hash, source_id
            )
            print(f"Quelle '{source_title}' aktualisiert. Alte Chunks geloescht.")
        else:
            # Neue Quelle anlegen
            source_id = await conn.fetchval("""
                INSERT INTO sources (title, source_type, url, hash, metadata)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """, source_title, source_type, source_url, text_hash,
                json.dumps({"language": "de", "version": "2024/1689"}))
            print(f"Quelle '{source_title}' angelegt (ID: {source_id}).")

        # Text in Chunks zerlegen
        chunks = chunk_legal_text(text, {
            "source": source_title,
            "source_type": source_type,
            "language": "de"
        })
        print(f"{len(chunks)} Chunks erzeugt.")

        # Embeddings erzeugen und speichern (in Batches von 50)
        batch_size = 50
        total_saved = 0

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [c["content"] for c in batch]

            print(f"  Batch {i // batch_size + 1}/{(len(chunks) - 1) // batch_size + 1}: "
                  f"Embeddings fuer {len(texts)} Chunks...")
            embeddings = create_embeddings(texts)

            for idx, (chunk, embedding) in enumerate(zip(batch, embeddings)):
                await conn.execute("""
                    INSERT INTO chunks (source_id, content, embedding, chunk_index, metadata)
                    VALUES ($1, $2, $3, $4, $5)
                """, source_id, chunk["content"], str(embedding),
                    i + idx, json.dumps(chunk["metadata"]))

            total_saved += len(batch)

        print(f"\nWissensbasis befuellt: {total_saved} Chunks gespeichert.")
        print(f"Quelle: {source_title} (ID: {source_id})")


async def main():
    parser = argparse.ArgumentParser(description="Wissensbasis befuellen")
    parser.add_argument("--file", "-f", help="Lokale Textdatei statt EUR-Lex Download")
    parser.add_argument("--title", "-t", default="EU AI Act", help="Titel der Quelle")
    args = parser.parse_args()

    if args.file:
        text = await load_from_file(args.file)
    else:
        text = await fetch_eu_ai_act()

    if len(text.strip()) < 100:
        print("FEHLER: Text ist zu kurz. Pruefe die Quelle.", file=sys.stderr)
        sys.exit(1)

    await seed_database(text, source_title=args.title)


if __name__ == "__main__":
    asyncio.run(main())
