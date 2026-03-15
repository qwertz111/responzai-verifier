# agents/uma_ux/usability_rules.py

import json
import anthropic
from json_repair import repair_json
from agents.uma_ux.prompt import UMA_SYSTEM_PROMPT
from pipeline.config import LLM_MODEL

client = anthropic.AsyncAnthropic()


async def review_usability(text: str, sections: list, structure_info: dict) -> dict:
    """
    Uma bewertet die Bedienungsfreundlichkeit eines Dokuments.

    Warum bekommen wir structure_info als separaten Parameter?
    Die regelbasierte Analyse in structure_analyzer.py liefert
    messbare Fakten (Abschnittslängen, fehlende Beispiele etc.).
    Uma (Claude) kann diese Fakten nutzen, muss sie aber im
    Kontext des vollständigen Texts interpretieren. Ein 500-Wort-
    Abschnitt ist problematisch in einem Formular, akzeptabel
    in einem Erklärungsdokument.

    Ablauf:
    1. Vollständiger Text, Abschnittsliste und Strukturanalyse
       werden als JSON an Claude übergeben.
    2. Uma bewertet nach ihren 7 Kriterien (Orientierung, Reihenfolge,
       Ausfüllhilfen, Gruppierung, Zuständigkeit, Vollständigkeit,
       Überforderung).
    3. Der Output priorisiert Verbesserungen nach Aufwand und Wirkung.

    temperature=0 stellt sicher, dass Uma reproduzierbar und
    ohne kreative Abweichungen bewertet.
    """
    user_message = json.dumps({
        "text": text,
        "sections": sections,
        "struktur_analyse": structure_info
    }, ensure_ascii=False, indent=2)

    response = await client.messages.create(
        model=LLM_MODEL,
        max_tokens=8192,
        temperature=0,
        system=UMA_SYSTEM_PROMPT,
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
        print(f"Uma: JSON-Parsing fehlgeschlagen ({e}). Gebe leeres Ergebnis zurück.")
        output = {"ux_issues": [], "ux_score": 0.0}

    return output
