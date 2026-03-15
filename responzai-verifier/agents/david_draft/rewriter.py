# agents/david_draft/rewriter.py

import json
import anthropic
from json_repair import repair_json
from agents.david_draft.prompt import DAVID_SYSTEM_PROMPT

client = anthropic.AsyncAnthropic()


async def rewrite_text(text: str, style_issues: list) -> dict:
    """
    David überarbeitet einen Text nach den responzai-Stilregeln.

    Warum übergeben wir die gefundenen Stilprobleme mit?
    Die regelbasierte Vorprüfung in style_guide.py findet einfache
    Muster. David (Claude) bekommt diese Liste als Hinweise, kann
    aber auch darüber hinaus sprachliche Probleme erkennen und
    im richtigen Kontext bewerten.

    Ablauf:
    1. Text und gefundene Stilprobleme werden als JSON übergeben.
    2. David erstellt einen strukturierten Diff aller Änderungen.
    3. Der Output enthält Lesbarkeits-Scores vor und nach der
       Überarbeitung sowie eine kompakte Zusammenfassung.

    temperature=0 stellt sicher, dass David reproduzierbar
    auf die gleichen Probleme reagiert.
    """
    user_message = json.dumps({
        "text": text,
        "gefundene_stilprobleme": style_issues
    }, ensure_ascii=False, indent=2)

    response = await client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=8192,
        temperature=0,
        system=DAVID_SYSTEM_PROMPT,
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

    try:
        output = json.loads(repair_json(raw))
    except Exception as e:
        print(f"David: JSON-Parsing fehlgeschlagen ({e}). Gebe leeres Ergebnis zurück.")
        output = {"text_improvements": [], "style_score": 0.0}

    return output
