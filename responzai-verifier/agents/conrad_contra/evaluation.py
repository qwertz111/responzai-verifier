# agents/conrad_contra/evaluation.py

from .prompt import CONRAD_SYSTEM_PROMPT
from .strategies import inverse_rag_search
from api.llm_client import call_llm
import json
from json_repair import repair_json


async def challenge_claim(claim: dict, vera_result: dict) -> dict:
    """
    Conrads Hauptfunktion: Versuche, den Claim zu widerlegen.
    """
    counter_evidence = await inverse_rag_search(claim["claim_text"])

    vera_context = "\n\n".join([
        f"[Veras Quelle: {p['source']}]\n{p['text']}"
        for p in vera_result.get("supporting_passages", [])
    ])

    counter_context = "\n\n".join([
        f"[Gegenrecherche: {chunk['source']}]\n{chunk['text']}"
        for chunk in counter_evidence
    ])

    user_message = f"""BEHAUPTUNG (von Vera als verifiziert eingestuft, Score: {vera_result.get('score', 0)}):
{claim['claim_text']}

VERAS QUELLENBELEGE:
{vera_context}

ERGEBNISSE DEINER GEGENRECHERCHE:
{counter_context}

Versuche diese Behauptung zu widerlegen. Wende alle vier Strategien an."""

    response_text = await call_llm(
        system=CONRAD_SYSTEM_PROMPT,
        user_message=user_message,
        max_tokens=2048,
    )

    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1

    if json_start == -1 or json_end == 0:
        return {"result": "survived", "reasoning": "Keine JSON-Antwort von Conrad"}

    try:
        result = json.loads(repair_json(response_text[json_start:json_end]))
    except Exception:
        return {"result": "survived", "reasoning": "JSON-Parsing fehlgeschlagen"}

    if "result" not in result:
        result["result"] = "survived"

    return result
