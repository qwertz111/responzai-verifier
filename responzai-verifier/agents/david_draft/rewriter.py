# agents/david_draft/rewriter.py

import json
from json_repair import repair_json
from agents.david_draft.prompt import DAVID_SYSTEM_PROMPT
from api.llm_client import call_llm


async def rewrite_text(text: str, style_issues: list) -> dict:
    """Davina überarbeitet einen Text nach den responzai-Stilregeln."""
    user_message = json.dumps({
        "text": text,
        "gefundene_stilprobleme": style_issues
    }, ensure_ascii=False, indent=2)

    try:
        raw = await call_llm(
            system=DAVID_SYSTEM_PROMPT,
            user_message=user_message,
            max_tokens=2048,
        )
    except Exception as e:
        print(f"Davina: API-Fehler ({e}).")
        return {"changes": [], "style_score": 0.0}

    raw = raw.strip()
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        output = json.loads(repair_json(raw))
    except Exception as e:
        print(f"Davina: JSON-Parsing fehlgeschlagen ({e}).")
        return {"changes": [], "style_score": 0.0}

    return output
