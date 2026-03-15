# agents/sven_sync/contradiction_map.py

import anthropic
import json
from json_repair import repair_json
from .prompt import SVEN_SYSTEM_PROMPT

client = anthropic.Anthropic()


async def check_contradictions(similar_pairs: list) -> dict:
    """
    Prüft ähnliche Claim-Paare auf tatsächliche Widersprüche.

    Warum ein eigener Schritt?
    Ähnlichkeit ist nicht gleich Widerspruch. Zwei Behauptungen
    können sich ähnlich sein und trotzdem dasselbe sagen - oder
    sich direkt widersprechen. Claude entscheidet, was zutrifft.

    Ablauf:
    1. Jedes ähnliche Paar wird einzeln an Claude geschickt
    2. Claude klassifiziert: Widerspruch, Duplikat oder beides
    3. Schweregrade werden gezählt und in den consistency_score eingerechnet

    consistency_score-Formel:
    1.0 - (critical * 0.3 + major * 0.15 + minor * 0.05)
    Minimum ist 0.0 (Score wird nicht negativ).
    """
    contradictions = []
    duplicates = []

    for pair in similar_pairs:
        claim_a = pair["claim_a"]
        claim_b = pair["claim_b"]
        similarity = pair["similarity"]

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            temperature=0,
            system=SVEN_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"""Vergleiche diese zwei Behauptungen und prüfe, ob sie sich widersprechen.

BEHAUPTUNG A (ID: {claim_a['id']}):
{claim_a['claim_text']}
Quelle: {claim_a.get('source_url', 'unbekannt')}

BEHAUPTUNG B (ID: {claim_b['id']}):
{claim_b['claim_text']}
Quelle: {claim_b.get('source_url', 'unbekannt')}

Ähnlichkeit: {similarity:.2f}

Antworte ausschließlich im vorgegebenen JSON-Format.
Wenn kein Widerspruch vorliegt, gib leere Listen zurück."""
                }
            ]
        )

        response_text = message.content[0].text
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1

        if json_start == -1:
            continue

        result = json.loads(repair_json(response_text[json_start:json_end]))

        contradictions.extend(result.get("contradictions", []))
        duplicates.extend(result.get("duplicates", []))

    # consistency_score berechnen
    critical_count = sum(1 for c in contradictions if c.get("severity") == "critical")
    major_count = sum(1 for c in contradictions if c.get("severity") == "major")
    minor_count = sum(1 for c in contradictions if c.get("severity") == "minor")

    penalty = critical_count * 0.3 + major_count * 0.15 + minor_count * 0.05
    consistency_score = max(0.0, 1.0 - penalty)

    return {
        "contradictions": contradictions,
        "duplicates": duplicates,
        "consistency_score": round(consistency_score, 4)
    }
