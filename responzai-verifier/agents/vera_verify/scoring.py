# agents/vera_verify/scoring.py

from .prompt import VERA_SYSTEM_PROMPT
from .rag_query import find_relevant_chunks
from api.llm_client import call_llm
import json
from json_repair import repair_json


async def verify_claim(claim: dict) -> dict:
    """
    Prüft eine einzelne Behauptung gegen die Wissensbasis.
    """
    relevant_chunks = await find_relevant_chunks(claim["claim_text"])

    # Top 5 fuer den LLM-Kontext (spart Tokens, behaelt Relevanz)
    top_chunks = relevant_chunks[:5]

    context = "\n\n".join([
        f"[Quelle: {chunk['source']}]\n{chunk['text']}"
        for chunk in top_chunks
    ])

    user_message = f"""BEHAUPTUNG:
{claim['claim_text']}

KATEGORIE: {claim['category']}

QUELLENPASSAGEN AUS DER WISSENSBASIS:
{context}

Bewerte diese Behauptung auf Basis der Quellenpassagen."""

    response_text = await call_llm(
        system=VERA_SYSTEM_PROMPT,
        user_message=user_message,
        max_tokens=2048,
    )

    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1

    if json_start == -1 or json_end == 0:
        return {"score": 0.0, "reasoning": "Keine JSON-Antwort von Vera", "supporting_passages": []}

    try:
        result = json.loads(repair_json(response_text[json_start:json_end]))
    except Exception:
        return {"score": 0.0, "reasoning": "JSON-Parsing fehlgeschlagen", "supporting_passages": []}

    # Sicherstellen dass score existiert
    if "score" not in result:
        result["score"] = 0.0

    return result
