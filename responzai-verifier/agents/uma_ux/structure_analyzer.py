# agents/uma_ux/structure_analyzer.py

import re


def analyze_structure(sections: list) -> dict:
    """
    Analysiert die Dokumentstruktur auf UX-Probleme.

    Eine gute Dokumentstruktur hilft Anwendern, sich schnell
    zu orientieren und die richtigen Stellen zu finden.
    Diese Analyse prüft mechanisch messbare Merkmale:
    - Gibt es eine sinnvolle Überschriftenhierarchie?
    - Sind einzelne Abschnitte zu lang?
    - Gibt es Beispiele und Ausfüllhilfen?

    Der Output wird an Uma (Claude) weitergegeben, die ihn im
    Kontext des vollständigen Textes bewertet.

    sections ist eine Liste von Dicts mit den Feldern:
    - title: Überschrift des Abschnitts (optional)
    - level: Überschriftsebene als int (1=H1, 2=H2 etc., optional)
    - content: Textinhalt des Abschnitts
    """
    if not sections:
        return {
            "total_sections": 0,
            "avg_length": 0,
            "has_examples": False,
            "structure_issues": ["Keine Abschnitte übergeben."]
        }

    structure_issues = []

    # Abschnittslängen berechnen (in Wörtern)
    lengths = []
    for section in sections:
        content = section.get("content", "")
        word_count = len(content.split())
        lengths.append(word_count)

    avg_length = sum(lengths) // len(lengths) if lengths else 0

    # Überschriftenhierarchie prüfen
    levels = [s.get("level") for s in sections if s.get("level") is not None]
    if levels:
        # Prüfen ob Ebenen übersprungen werden (z.B. H1 direkt zu H3)
        for i in range(1, len(levels)):
            if levels[i] - levels[i - 1] > 1:
                structure_issues.append(
                    f"Überschriftenebene übersprungen: von H{levels[i-1]} zu H{levels[i]}. "
                    "Das erschwert die Navigation."
                )
                break

    # Zu lange Abschnitte identifizieren
    for i, (section, word_count) in enumerate(zip(sections, lengths)):
        if word_count > 400:
            title = section.get("title", f"Abschnitt {i + 1}")
            structure_issues.append(
                f"'{title}' hat {word_count} Wörter. "
                "Abschnitte über 400 Wörter sollten aufgeteilt werden."
            )

    # Abschnitte ohne Überschrift prüfen
    untitled = sum(1 for s in sections if not s.get("title", "").strip())
    if untitled > 0:
        structure_issues.append(
            f"{untitled} Abschnitt(e) ohne Überschrift. "
            "Jeder Abschnitt braucht eine beschreibende Überschrift."
        )

    # Prüfen ob Beispiele oder Ausfüllhilfen vorhanden sind
    # Typische Signalwörter: "Beispiel", "z.B.", "z. B.", "etwa", "Muster", "Vorlage"
    example_patterns = [
        r"\bBeispiel\b",
        r"\bz\.\s*B\.\b",
        r"\betwa\b",
        r"\bMuster\b",
        r"\bVorlage\b",
        r"\bHinweis\b",
        r"\bAusfüllhilfe\b",
    ]
    full_text = " ".join(s.get("content", "") for s in sections)
    has_examples = any(re.search(p, full_text, re.IGNORECASE) for p in example_patterns)

    if not has_examples:
        structure_issues.append(
            "Keine Beispiele oder Ausfüllhilfen gefunden. "
            "Anwender brauchen konkrete Beispiele, um Felder korrekt auszufüllen."
        )

    return {
        "total_sections": len(sections),
        "avg_length": avg_length,
        "has_examples": has_examples,
        "structure_issues": structure_issues
    }
