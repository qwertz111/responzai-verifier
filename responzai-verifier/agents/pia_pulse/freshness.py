# agents/pia_pulse/freshness.py

import json
from json_repair import repair_json
from .prompt import PIA_SYSTEM_PROMPT
from .monitors import check_eurlex_updates
from api.llm_client import call_llm


async def analyze_freshness(claim: dict) -> dict:
    """Analysiert Zeitbezüge in einer Behauptung und bewertet ihre Aktualität."""
    eurlex_updates = check_eurlex_updates()

    updates_context = ""
    if eurlex_updates:
        recent = eurlex_updates[:5]
        updates_context = "\n".join([
            f"- {u['published']}: {u['title']} ({u['url']})"
            for u in recent
        ])
    else:
        updates_context = "Keine aktuellen EUR-Lex-Updates verfügbar."

    default_result = {
        "claim_id": claim.get("id", "unbekannt"),
        "time_references": [],
        "freshness": "fresh",
        "source_last_updated": None,
        "latest_version_available": None,
        "days_since_update": None,
        "upcoming_deadlines": [],
        "update_suggestion": None
    }

    try:
        response_text = await call_llm(
            system=PIA_SYSTEM_PROMPT,
            user_message=f"""Prüfe diese Behauptung auf Zeitbezüge und Aktualität.

BEHAUPTUNG (ID: {claim.get('id', 'unbekannt')}):
{claim.get('claim_text', '')}

AKTUELLE EUR-LEX-VERÖFFENTLICHUNGEN:
{updates_context}

Antworte ausschließlich im vorgegebenen JSON-Format.""",
            max_tokens=1024,
        )
    except Exception as e:
        print(f"Pia: API-Fehler ({e}). Gebe default zurück.")
        return default_result

    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1

    if json_start == -1:
        return default_result

    try:
        result = json.loads(repair_json(response_text[json_start:json_end]))
    except Exception:
        return default_result

    result["claim_id"] = claim.get("id", result.get("claim_id", "unbekannt"))
    return result
