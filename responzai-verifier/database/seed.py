# database/seed.py

"""
Wissensbasis befuellen mit Rechtstexten und anderen Quellen.

Verwendung:
    python -m database.seed                                        # EU AI Act von EUR-Lex
    python -m database.seed --file path.txt --title "DSGVO"        # Lokale Textdatei
    python -m database.seed --url "https://..." --title "DSGVO"    # Beliebige Webseite
    python -m database.seed --list                                 # Alle Quellen anzeigen
    python -m database.seed --delete "DSGVO"                       # Quelle loeschen

Vordefinierte Quellen (Kurzform):
    python -m database.seed --source dsgvo
    python -m database.seed --source ki-haftung
    python -m database.seed --source all                           # Alle vordefinierten laden
"""

import argparse
import asyncio
import hashlib
import json
import re
import sys
from html.parser import HTMLParser

import httpx

from database.connection import get_connection
from processing.chunking import chunk_legal_text
from processing.embedding import create_embeddings


# Vordefinierte Quellen
PREDEFINED_SOURCES = {
    "eu-ai-act": {
        "title": "EU AI Act",
        "url": "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024R1689",
        "type": "primary",
        "description": "Verordnung (EU) 2024/1689 - KI-Verordnung",
    },
    "dsgvo": {
        "title": "DSGVO",
        "url": "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32016R0679",
        "type": "primary",
        "description": "Datenschutz-Grundverordnung (EU) 2016/679",
    },
    "ki-haftung": {
        "title": "KI-Haftungsrichtlinie",
        "url": "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:52022PC0496",
        "type": "secondary",
        "description": "Vorschlag fuer eine Richtlinie ueber KI-Haftung",
    },
    "produkthaftung": {
        "title": "Produkthaftungsrichtlinie",
        "url": "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024L2853",
        "type": "secondary",
        "description": "Richtlinie (EU) 2024/2853 ueber Produkthaftung",
    },
}


class HTMLTextExtractor(HTMLParser):
    """Extrahiert lesbaren Text aus HTML, ignoriert Scripts/Styles/Navigation."""

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


async def fetch_url(url: str, title: str = "") -> str:
    """Laedt eine Webseite und extrahiert den Text."""
    label = title or url
    print(f"Lade '{label}' von {url}...")

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()

    extractor = HTMLTextExtractor()
    extractor.feed(response.text)
    text = extractor.get_text()

    print(f"Geladen: {len(text)} Zeichen, ~{len(text.split())} Woerter")
    return text


async def load_from_file(filepath: str) -> str:
    """Laedt Text aus einer lokalen Datei."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    print(f"Datei geladen: {filepath} ({len(text)} Zeichen)")
    return text


async def seed_database(text: str, source_title: str = "EU AI Act",
                         source_type: str = "primary",
                         source_url: str = ""):
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
            source_id = existing["id"]
            await conn.execute(
                "DELETE FROM chunks WHERE source_id = $1", source_id
            )
            await conn.execute(
                "UPDATE sources SET hash = $1, fetched_at = NOW() WHERE id = $2",
                text_hash, source_id
            )
            print(f"Quelle '{source_title}' aktualisiert. Alte Chunks geloescht.")
        else:
            source_id = await conn.fetchval("""
                INSERT INTO sources (title, source_type, url, hash, metadata)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """, source_title, source_type, source_url, text_hash,
                json.dumps({"language": "de"}))
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


async def list_sources():
    """Zeigt alle Quellen in der Datenbank an."""
    async with get_connection() as conn:
        rows = await conn.fetch(
            "SELECT s.id, s.title, s.source_type, s.url, s.fetched_at, "
            "(SELECT count(*) FROM chunks c WHERE c.source_id = s.id) as chunk_count "
            "FROM sources s ORDER BY s.id"
        )

    if not rows:
        print("Keine Quellen in der Datenbank.")
        return

    print(f"\n{'ID':<4} {'Titel':<30} {'Typ':<10} {'Chunks':<8} {'Geladen am'}")
    print("-" * 80)
    for row in rows:
        fetched = row["fetched_at"].strftime("%Y-%m-%d %H:%M") if row["fetched_at"] else "-"
        print(f"{row['id']:<4} {row['title']:<30} {row['source_type']:<10} "
              f"{row['chunk_count']:<8} {fetched}")

    print(f"\nGesamt: {len(rows)} Quellen, "
          f"{sum(r['chunk_count'] for r in rows)} Chunks")


async def delete_source(title: str):
    """Loescht eine Quelle und ihre Chunks."""
    async with get_connection() as conn:
        existing = await conn.fetchrow(
            "SELECT id FROM sources WHERE title = $1", title
        )
        if not existing:
            print(f"Quelle '{title}' nicht gefunden.")
            return

        source_id = existing["id"]
        deleted_chunks = await conn.execute(
            "DELETE FROM chunks WHERE source_id = $1", source_id
        )
        await conn.execute("DELETE FROM sources WHERE id = $1", source_id)
        print(f"Quelle '{title}' (ID: {source_id}) und alle Chunks geloescht.")


async def main():
    parser = argparse.ArgumentParser(
        description="Wissensbasis befuellen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Vordefinierte Quellen:
  eu-ai-act     EU AI Act (Verordnung 2024/1689)
  dsgvo         Datenschutz-Grundverordnung (2016/679)
  ki-haftung    KI-Haftungsrichtlinie (Vorschlag)
  produkthaftung  Produkthaftungsrichtlinie (2024/2853)
  all           Alle vordefinierten Quellen laden
        """
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--file", "-f", help="Lokale Textdatei laden")
    group.add_argument("--url", "-u", help="Webseite laden (HTML wird zu Text konvertiert)")
    group.add_argument("--source", "-s", help="Vordefinierte Quelle laden (z.B. dsgvo, all)")
    group.add_argument("--list", "-l", action="store_true", help="Alle Quellen anzeigen")
    group.add_argument("--delete", "-d", help="Quelle nach Titel loeschen")

    parser.add_argument("--title", "-t", help="Titel der Quelle (bei --file oder --url)")
    parser.add_argument("--type", dest="source_type", default="primary",
                        choices=["primary", "secondary", "own"],
                        help="Quellentyp (default: primary)")

    args = parser.parse_args()

    # --list
    if args.list:
        await list_sources()
        return

    # --delete
    if args.delete:
        await delete_source(args.delete)
        return

    # --source (vordefiniert)
    if args.source:
        if args.source == "all":
            for key, src in PREDEFINED_SOURCES.items():
                print(f"\n{'='*60}")
                print(f"Lade: {src['title']} ({src['description']})")
                print(f"{'='*60}")
                text = await fetch_url(src["url"], src["title"])
                if len(text.strip()) < 100:
                    print(f"WARNUNG: Text fuer '{src['title']}' zu kurz, uebersprungen.",
                          file=sys.stderr)
                    continue
                await seed_database(text, src["title"], src["type"], src["url"])
            return

        if args.source not in PREDEFINED_SOURCES:
            print(f"Unbekannte Quelle: '{args.source}'. "
                  f"Verfuegbar: {', '.join(PREDEFINED_SOURCES.keys())}, all",
                  file=sys.stderr)
            sys.exit(1)

        src = PREDEFINED_SOURCES[args.source]
        text = await fetch_url(src["url"], src["title"])
        if len(text.strip()) < 100:
            print("FEHLER: Text ist zu kurz. Pruefe die Quelle.", file=sys.stderr)
            sys.exit(1)
        await seed_database(text, src["title"], src["type"], src["url"])
        return

    # --url
    if args.url:
        title = args.title or args.url
        text = await fetch_url(args.url, title)
        if len(text.strip()) < 100:
            print("FEHLER: Text ist zu kurz. Pruefe die Quelle.", file=sys.stderr)
            sys.exit(1)
        await seed_database(text, title, args.source_type, args.url)
        return

    # --file
    if args.file:
        title = args.title or args.file
        text = await load_from_file(args.file)
        if len(text.strip()) < 100:
            print("FEHLER: Text ist zu kurz. Pruefe die Quelle.", file=sys.stderr)
            sys.exit(1)
        await seed_database(text, title, args.source_type, "")
        return

    # Default: EU AI Act
    src = PREDEFINED_SOURCES["eu-ai-act"]
    text = await fetch_url(src["url"], src["title"])
    if len(text.strip()) < 100:
        print("FEHLER: Text ist zu kurz. Pruefe die Quelle.", file=sys.stderr)
        sys.exit(1)
    await seed_database(text, src["title"], src["type"], src["url"])


if __name__ == "__main__":
    asyncio.run(main())
