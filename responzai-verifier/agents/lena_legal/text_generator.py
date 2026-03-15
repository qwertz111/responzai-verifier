# agents/lena_legal/text_generator.py

import json
from json_repair import repair_json
from agents.lena_legal.prompt import LENA_SYSTEM_PROMPT
from api.llm_client import call_llm
from pipeline.config import LLM_MODEL_STRONG


async def generate_legal_update(claim: dict, sources: list) -> dict:
    """Lena erstellt einen Textverbesserungsvorschlag auf Basis der Quellen."""
    source_passages = [
        {"hash": s["hash"], "text": s["text"], "source": s["source"]}
        for s in sources
    ]

    user_message = json.dumps({
        "claim": claim,
        "source_passages": source_passages
    }, ensure_ascii=False, indent=2)

    try:
        raw = await call_llm(
            system=LENA_SYSTEM_PROMPT,
            user_message=user_message,
            model=LLM_MODEL_STRONG,
            max_tokens=2048,
        )
    except Exception as e:
        return {"status": "ERROR", "reason": f"API-Fehler: {e}"}

    raw = raw.strip()
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        output = json.loads(repair_json(raw))
    except Exception:
        return {"status": "ERROR", "reason": "JSON-Parsing fehlgeschlagen"}

    source_hash_map = {s["hash"]: s for s in sources}
    for ref in output.get("sources_used", []):
        ref_hash = ref.get("hash", "")
        if ref_hash in source_hash_map:
            ref["source"] = source_hash_map[ref_hash]["source"]

    return output
