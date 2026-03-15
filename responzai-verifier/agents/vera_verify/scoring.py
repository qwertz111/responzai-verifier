# agents/vera_verify/scoring.py

import anthropic
from .prompt import VERA_SYSTEM_PROMPT
from .rag_query import find_relevant_chunks
import json
from json_repair import repair_json

client = anthropic.AsyncAnthropic()

async def verify_claim(claim: dict) -> dict:
    """
    Prüft eine einzelne Behauptung gegen die Wissensbasis.

    Ablauf:
    1. Relevante Quellenpassagen finden (RAG)
    2. Behauptung + Quellen an Claude schicken
    3. Bewertung zurückbekommen
    """
    # Schritt 1: Relevante Stellen finden
    relevant_chunks = await find_relevant_chunks(claim["claim_text"])

    # Schritt 2: Quellen als Kontext aufbereiten
    context = "\n\n".join([
        f"[Quelle: {chunk['source']}]\n{chunk['text']}"
        for chunk in relevant_chunks
    ])

    # Schritt 3: An Claude schicken
    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        temperature=0,
        system=VERA_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""BEHAUPTUNG:
{claim['claim_text']}

KATEGORIE: {claim['category']}

QUELLENPASSAGEN AUS DER WISSENSBASIS:
{context}

Bewerte diese Behauptung auf Basis der Quellenpassagen."""
            }
        ]
    )

    # Ergebnis parsen
    response_text = message.content[0].text
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1
    result = json.loads(repair_json(response_text[json_start:json_end]))

    return result
