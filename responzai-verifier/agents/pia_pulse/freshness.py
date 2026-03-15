# agents/pia_pulse/freshness.py

import anthropic
import json
from json_repair import repair_json
from .prompt import PIA_SYSTEM_PROMPT
from .monitors import check_eurlex_updates

client = anthropic.AsyncAnthropic()


async def analyze_freshness(claim: dict) -> dict:
    """
    Analysiert Zeitbezüge in einer Behauptung und bewertet ihre Aktualität.

    Ablauf:
    1. EUR-Lex RSS-Feed auf neue Veröffentlichungen prüfen
    2. Behauptung + aktuelle EUR-Lex-Updates an Claude schicken
    3. Claude findet Zeitbezüge und bewertet die Aktualität

    Warum zuerst EUR-Lex prüfen?
    Claude kann nur beurteilen, ob eine Behauptung veraltet ist,
    wenn es weiß, was inzwischen veröffentlicht wurde.
    Die EUR-Lex-Updates geben diesen Kontext.
    """
    # Schritt 1: Aktuelle EUR-Lex-Updates abrufen
    eurlex_updates = check_eurlex_updates()

    # Updates als lesbaren Kontext aufbereiten (max. 5 neueste)
    updates_context = ""
    if eurlex_updates:
        recent = eurlex_updates[:5]
        updates_context = "\n".join([
            f"- {u['published']}: {u['title']} ({u['url']})"
            for u in recent
        ])
    else:
        updates_context = "Keine aktuellen EUR-Lex-Updates verfügbar."

    # Schritt 2: An Claude schicken
    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        temperature=0,
        system=PIA_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""Prüfe diese Behauptung auf Zeitbezüge und Aktualität.

BEHAUPTUNG (ID: {claim.get('id', 'unbekannt')}):
{claim.get('claim_text', '')}

AKTUELLE EUR-LEX-VERÖFFENTLICHUNGEN:
{updates_context}

Antworte ausschließlich im vorgegebenen JSON-Format."""
            }
        ]
    )

    # Ergebnis parsen
    response_text = message.content[0].text
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1

    if json_start == -1:
        # Fallback, wenn kein JSON zurückkommt
        return {
            "claim_id": claim.get("id", "unbekannt"),
            "time_references": [],
            "freshness": "fresh",
            "source_last_updated": None,
            "latest_version_available": None,
            "days_since_update": None,
            "upcoming_deadlines": [],
            "update_suggestion": None
        }

    result = json.loads(repair_json(response_text[json_start:json_end]))

    # claim_id sicherstellen (Claude könnte sie weglassen)
    result["claim_id"] = claim.get("id", result.get("claim_id", "unbekannt"))

    return result
