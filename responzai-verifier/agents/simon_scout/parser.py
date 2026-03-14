# agents/simon_scout/parser.py

import anthropic
from .prompt import SIMON_SYSTEM_PROMPT
import json
from json_repair import repair_json

client = anthropic.Anthropic()

# Automatisches Chunking ab dieser Textlänge (Zeichen)
CHUNK_THRESHOLD = 60_000   # ~15.000 Tokens Input
CHUNK_SIZE      = 40_000   # ~10.000 Tokens pro Chunk
CHUNK_OVERLAP   = 2_000    # ~500 Tokens Overlap (Satzgrenzen abfangen)


def _split_chunks(text: str) -> list[str]:
    """
    Zerlegt einen langen Text in überlappende Chunks.

    Warum auf Absatzgrenzen splitten?
    Claims erstrecken sich selten über Absatzgrenzen hinaus.
    Ein Absatz-Split reduziert die Chance, dass ein Claim
    genau an der Chunk-Grenze abgeschnitten wird.
    Der Overlap fängt den Rest ab.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        if end < len(text):
            # Auf den letzten Absatzumbruch vor end zurückgehen
            boundary = text.rfind("\n\n", start, end)
            if boundary == -1:
                boundary = text.rfind("\n", start, end)
            if boundary != -1 and boundary > start + CHUNK_SIZE // 2:
                end = boundary
        chunks.append(text[start:end])
        start = end - CHUNK_OVERLAP
    return chunks


async def _extract_from_chunk(chunk: str, source_url: str, id_offset: int) -> list[dict]:
    """Ruft Claude für einen einzelnen Chunk auf und gibt die Claims zurück."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        temperature=0,
        system=SIMON_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""Analysiere diesen Text und extrahiere
                alle prüfbaren Behauptungen.

                URL: {source_url}

                TEXT:
                {chunk}
                """
            }
        ]
    )

    response_text = message.content[0].text
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1

    if json_start == -1 or json_end == 0:
        return []

    try:
        data = json.loads(repair_json(response_text[json_start:json_end]))
    except Exception as e:
        print(f"Simon: JSON-Parsing fehlgeschlagen in Chunk ({e}).")
        return []

    claims = data.get("claims", [])

    # IDs neu vergeben damit keine Kollisionen zwischen Chunks entstehen
    for i, claim in enumerate(claims):
        claim["id"] = f"claim_{id_offset + i + 1:03d}"

    return claims


def _deduplicate(claims: list[dict]) -> list[dict]:
    """
    Entfernt doppelte Claims, die durch den Chunk-Overlap entstehen können.

    Strategie: Zwei Claims gelten als Duplikat, wenn die ersten 80 Zeichen
    ihres claim_text identisch sind (nach Normalisierung).
    Das ist schnell und trifft die relevanten Fälle ohne NLP-Overhead.
    """
    seen = set()
    unique = []
    for claim in claims:
        key = claim.get("claim_text", "")[:80].strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(claim)
    return unique


async def extract_claims(text: str, source_url: str) -> dict:
    """
    Schickt den Text an Claude und bekommt strukturierte Claims zurück.

    Warum temperature=0?
    Wir wollen, dass Simon bei demselben Text immer dieselben
    Behauptungen findet. Kreativität ist hier nicht erwünscht.
    Reproduzierbarkeit ist wichtiger.

    Warum automatisches Chunking?
    Bei Dokumenten > 60.000 Zeichen (~150 KB reiner Text) wird
    der Text in Chunks von je 40.000 Zeichen mit 2.000 Zeichen
    Overlap aufgeteilt. So bleibt die Output-Qualität konstant
    und der 8192-Token-Limit des Outputs wird nicht gesprengt.
    """
    if len(text) <= CHUNK_THRESHOLD:
        # Kurzer Text: direkt verarbeiten
        return await _extract_single(text, source_url)

    # Langer Text: Chunking
    chunks = _split_chunks(text)
    print(f"Simon: Text zu lang ({len(text)} Zeichen), aufgeteilt in {len(chunks)} Chunks.")

    all_claims = []
    for i, chunk in enumerate(chunks):
        chunk_claims = await _extract_from_chunk(chunk, source_url, len(all_claims))
        print(f"Simon: Chunk {i+1}/{len(chunks)} → {len(chunk_claims)} Claims.")
        all_claims.extend(chunk_claims)

    all_claims = _deduplicate(all_claims)
    print(f"Simon: {len(all_claims)} Claims nach Deduplizierung.")

    return {
        "claims": all_claims,
        "summary": {
            "total_claims": len(all_claims),
            "chunks_processed": len(chunks),
        }
    }


async def _extract_single(text: str, source_url: str) -> dict:
    """Verarbeitet einen kurzen Text ohne Chunking."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        temperature=0,
        system=SIMON_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""Analysiere diesen Text und extrahiere
                alle prüfbaren Behauptungen.

                URL: {source_url}

                TEXT:
                {text}
                """
            }
        ]
    )

    response_text = message.content[0].text
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1

    if json_start == -1 or json_end == 0:
        print(f"Simon: Kein JSON in Antwort gefunden. Gebe leere Claims zurück.")
        return {"claims": []}

    try:
        claims_data = json.loads(repair_json(response_text[json_start:json_end]))
    except Exception as e:
        print(f"Simon: JSON-Parsing fehlgeschlagen ({e}). Gebe leere Claims zurück.")
        return {"claims": []}

    return claims_data
