# agents/simon_scout/parser.py

import anthropic
from .prompt import SIMON_SYSTEM_PROMPT
import json

client = anthropic.Anthropic()

async def extract_claims(text: str, source_url: str) -> dict:
    """
    Schickt den Text an Claude und bekommt strukturierte Claims zurück.

    Warum temperature=0?
    Wir wollen, dass Simon bei demselben Text immer dieselben
    Behauptungen findet. Kreativität ist hier nicht erwünscht.
    Reproduzierbarkeit ist wichtiger.
    """
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
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

    # Antwort parsen
    response_text = message.content[0].text

    # JSON aus der Antwort extrahieren
    # (Claude gibt manchmal Text vor/nach dem JSON zurück)
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1
    claims_data = json.loads(response_text[json_start:json_end])

    return claims_data
