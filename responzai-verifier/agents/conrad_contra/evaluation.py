# agents/conrad_contra/evaluation.py

from .prompt import CONRAD_SYSTEM_PROMPT
from .strategies import inverse_rag_search
import anthropic
import json

client = anthropic.Anthropic()

async def challenge_claim(claim: dict, vera_result: dict) -> dict:
    """
    Conrads Hauptfunktion: Versuche, den Claim zu widerlegen.

    Conrad bekommt:
    - Den Claim selbst
    - Veras Ergebnis (Score, Quellenpassagen)
    - Eigene Gegenrecherche-Ergebnisse
    """
    # Eigene Gegenrecherche durchführen
    counter_evidence = await inverse_rag_search(claim["claim_text"])

    # Kontext aufbereiten
    vera_context = "\n\n".join([
        f"[Veras Quelle: {p['source']}]\n{p['text']}"
        for p in vera_result.get("supporting_passages", [])
    ])

    counter_context = "\n\n".join([
        f"[Gegenrecherche: {chunk['source']}]\n{chunk['text']}"
        for chunk in counter_evidence
    ])

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        temperature=0,
        system=CONRAD_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""BEHAUPTUNG (von Vera als verifiziert eingestuft, Score: {vera_result['score']}):
{claim['claim_text']}

VERAS QUELLENBELEGE:
{vera_context}

ERGEBNISSE DEINER GEGENRECHERCHE:
{counter_context}

Versuche diese Behauptung zu widerlegen. Wende alle vier Strategien an."""
            }
        ]
    )

    response_text = message.content[0].text
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1
    result = json.loads(response_text[json_start:json_end])

    return result
