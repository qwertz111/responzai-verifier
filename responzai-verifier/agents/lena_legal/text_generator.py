# agents/lena_legal/text_generator.py

import json
import anthropic
from agents.lena_legal.prompt import LENA_SYSTEM_PROMPT

client = anthropic.Anthropic()


async def generate_legal_update(claim: dict, sources: list) -> dict:
    """
    Lena erstellt einen Textverbesserungsvorschlag auf Basis
    der gefundenen Quellen.

    Warum temperature=0?
    Juristische Texte dulden keine Kreativität. Jede Abweichung
    vom tatsächlichen Quelleninhalt wäre eine Halluzination.
    temperature=0 erzwingt den deterministischsten möglichen Output.

    Ablauf:
    1. Claim und Quellstellen werden als JSON an Claude übergeben.
    2. Claude gibt einen strukturierten Diff zurück (was steht da,
       was soll da stehen, warum).
    3. Die Source-Hashes aus unserer Quellliste werden zum Output
       hinzugefügt, damit verification_loop.py sie prüfen kann.
    """
    source_passages = [
        {
            "hash": s["hash"],
            "text": s["text"],
            "source": s["source"]
        }
        for s in sources
    ]

    user_message = json.dumps({
        "claim": claim,
        "source_passages": source_passages
    }, ensure_ascii=False, indent=2)

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        temperature=0,
        system=LENA_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    raw = response.content[0].text.strip()

    # JSON-Block extrahieren falls Claude Prosa darum herum schreibt
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    output = json.loads(raw)

    # Source-Hashes aus der gemappten Liste eintragen
    # damit verification_loop.py sie gegen die bekannten Hashes prüfen kann
    source_hash_map = {s["hash"]: s for s in sources}
    for ref in output.get("sources_used", []):
        ref_hash = ref.get("hash", "")
        if ref_hash in source_hash_map:
            ref["source"] = source_hash_map[ref_hash]["source"]

    return output
