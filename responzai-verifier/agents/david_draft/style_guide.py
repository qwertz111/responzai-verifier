# agents/david_draft/style_guide.py

import re

# Stilregeln des responzai-Standards.
# Jeder Eintrag beschreibt ein Problem und gibt einen Hinweis zur Behebung.
# Die Patterns werden in check_style() gegen den Text geprüft.
STYLE_RULES = {
    "passive_voice": {
        "description": "Passivkonstruktionen sind schwerer lesbar als Aktivsätze.",
        "patterns": [
            r"wird\s+\w+\s+gemacht",
            r"ist\s+\w+\s*zu\s+\w+",
            r"ist\s+sicherzustellen",
            r"ist\s+zu\s+prüfen",
            r"ist\s+zu\s+beachten",
            r"ist\s+zu\s+erstellen",
            r"ist\s+zu\s+dokumentieren",
            r"werden\s+\w+",
        ],
        "suggestion": "Aktiv formulieren: 'Prüfen Sie...' statt 'Es ist zu prüfen...'",
    },
    "long_sentences": {
        "description": "Sätze über 20 Wörter sind schwer verständlich.",
        "threshold": 20,
        "suggestion": "Satz aufteilen. Maximal 15 Wörter pro Satz anstreben.",
    },
    "jargon": {
        "description": "Fachbegriffe ohne Erklärung schließen Leser aus.",
        "patterns": [
            r"\bImplementierung\b",
            r"\bOperationalisierung\b",
            r"\bKonsolidierung\b",
            r"\bSynergien\b",
            r"\bNachhaltigkeitsagenda\b",
        ],
        "suggestion": "Fachbegriff verwenden, aber sofort im nächsten Satz erklären.",
    },
    "nominalization": {
        "description": "Nominalstil macht Texte schwerfällig.",
        "patterns": [
            r"\w+ierung\b",
            r"\w+ung\b",
            r"\w+heit\b",
            r"\w+keit\b",
        ],
        "suggestion": "Verb statt Substantiv: 'implementieren' statt 'Implementierung'.",
    },
    "banned_words": {
        "description": "Verbotene Formulierungen laut responzai-Stilguide.",
        "words": [
            "Hand aufs Herz",
            "Technikgewitter",
            "Cloudnebel",
            " - ",   # Gedankenstrich mit Leerzeichen
        ],
        "suggestion": "Verbotenen Ausdruck streichen oder sachlich umformulieren.",
    },
}


def check_style(text: str) -> list:
    """
    Prüft einen Text gegen die responzai-Stilregeln.

    Gibt eine Liste von Problemen zurück. Jedes Problem enthält:
    - type: Welche Regelkategorie verletzt wurde
    - text: Die betroffene Textstelle
    - suggestion: Konkrete Verbesserungsempfehlung

    Hinweis: Dies ist eine regelbasierte Vorprüfung. Davina (Claude)
    bewertet die gefundenen Stellen anschließend in ihrem Kontext
    und entscheidet, ob und wie sie geändert werden sollen.
    """
    issues = []

    # Passiv-Konstruktionen prüfen
    passive_patterns = STYLE_RULES["passive_voice"]["patterns"]
    for pattern in passive_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            issues.append({
                "type": "passive_voice",
                "text": match.group(0),
                "suggestion": STYLE_RULES["passive_voice"]["suggestion"]
            })

    # Satzlänge prüfen
    # Sätze werden grob an Punkt, Ausrufe- und Fragezeichen aufgeteilt
    sentences = re.split(r'[.!?]+', text)
    for sentence in sentences:
        words = sentence.strip().split()
        if len(words) > STYLE_RULES["long_sentences"]["threshold"]:
            issues.append({
                "type": "long_sentences",
                "text": sentence.strip()[:120] + ("..." if len(sentence.strip()) > 120 else ""),
                "suggestion": STYLE_RULES["long_sentences"]["suggestion"]
            })

    # Verbotene Wörter prüfen
    for banned in STYLE_RULES["banned_words"]["words"]:
        if banned in text:
            issues.append({
                "type": "banned_words",
                "text": banned,
                "suggestion": STYLE_RULES["banned_words"]["suggestion"]
            })

    # Nominalstil prüfen (nur auffällige Häufungen, nicht jeden Treffer)
    nominalization_count = 0
    for pattern in STYLE_RULES["nominalization"]["patterns"]:
        matches = re.findall(pattern, text, re.IGNORECASE)
        nominalization_count += len(matches)

    if nominalization_count >= 3:
        issues.append({
            "type": "nominalization",
            "text": f"{nominalization_count} Nominalisierungen gefunden",
            "suggestion": STYLE_RULES["nominalization"]["suggestion"]
        })

    return issues
