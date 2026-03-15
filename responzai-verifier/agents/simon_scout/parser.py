# agents/simon_scout/parser.py

import asyncio
from .prompt import SIMON_SYSTEM_PROMPT
from api.llm_client import call_llm
import json
from json_repair import repair_json

# Automatisches Chunking ab dieser Textlänge (Zeichen)
CHUNK_THRESHOLD = 60_000   # ~15.000 Tokens Input
CHUNK_SIZE      = 40_000   # ~10.000 Tokens pro Chunk
CHUNK_OVERLAP   = 2_000    # ~500 Tokens Overlap (Satzgrenzen abfangen)


def _split_chunks(text: str) -> list[str]:
    """Zerlegt einen langen Text in überlappende Chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        if end < len(text):
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
    try:
        response_text = await call_llm(
            system=SIMON_SYSTEM_PROMPT,
            user_message=f"""Analysiere diesen Text und extrahiere alle prüfbaren Behauptungen.

URL: {source_url}

TEXT:
{chunk}""",
            max_tokens=4096,
        )
    except Exception as e:
        print(f"Simon: API-Fehler in Chunk ({e}).")
        return []

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
    for i, claim in enumerate(claims):
        claim["id"] = f"claim_{id_offset + i + 1:03d}"

    return claims


def _deduplicate(claims: list[dict]) -> list[dict]:
    """Entfernt doppelte Claims die durch Chunk-Overlap entstehen."""
    seen = set()
    unique = []
    for claim in claims:
        key = claim.get("claim_text", "")[:80].strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(claim)
    return unique


async def extract_claims(text: str, source_url: str) -> dict:
    """Extrahiert Claims aus Text. Bei langen Texten automatisches Chunking."""
    if len(text) <= CHUNK_THRESHOLD:
        return await _extract_single(text, source_url)

    chunks = _split_chunks(text)
    print(f"Simon: Text zu lang ({len(text)} Zeichen), aufgeteilt in {len(chunks)} Chunks.")

    # Chunks sequentiell verarbeiten (Rate Limit schonen)
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
    try:
        response_text = await call_llm(
            system=SIMON_SYSTEM_PROMPT,
            user_message=f"""Analysiere diesen Text und extrahiere alle prüfbaren Behauptungen.

URL: {source_url}

TEXT:
{text}""",
            max_tokens=4096,
        )
    except Exception as e:
        print(f"Simon: API-Fehler ({e}). Gebe leere Claims zurück.")
        return {"claims": []}

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
