# agents/uma_ux/usability_rules.py

import json
from json_repair import repair_json
from agents.uma_ux.prompt import UMA_SYSTEM_PROMPT
from api.llm_client import call_llm


async def review_usability(text: str, sections: list, structure_info: dict) -> dict:
    """Uma bewertet die Bedienungsfreundlichkeit eines Dokuments."""
    user_message = json.dumps({
        "text": text,
        "sections": sections,
        "struktur_analyse": structure_info
    }, ensure_ascii=False, indent=2)

    try:
        raw = await call_llm(
            system=UMA_SYSTEM_PROMPT,
            user_message=user_message,
            max_tokens=2048,
        )
    except Exception as e:
        print(f"Uma: API-Fehler ({e}).")
        return {"issues": [], "ux_score": 0.0}

    raw = raw.strip()
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        output = json.loads(repair_json(raw))
    except Exception as e:
        print(f"Uma: JSON-Parsing fehlgeschlagen ({e}).")
        return {"issues": [], "ux_score": 0.0}

    return output
