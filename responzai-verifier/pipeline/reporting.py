# pipeline/reporting.py

from datetime import datetime
from collections import Counter


def create_verification_report(state: dict) -> dict:
    """
    Erstellt den Verifikationsbericht nach Abschluss der Prüfphase.

    Fasst die Ergebnisse aller Prüfagenten zusammen:
    - Wie viele Claims wurden gefunden und geprüft?
    - Wie hoch ist die Konsistenz?
    - Wie aktuell sind die Quellen?
    - Wie verteilen sich Claims auf Kategorien?
    - Wie ist der Gesamtscore?

    overall_score-Gewichtung:
    - 40% Verifizierungsrate (Vera)
    - 30% Überlebensrate nach Conrad
    - 20% Konsistenz (Sven)
    - 10% Aktualität (Pia)
    """
    claims = state.get("claims", [])
    survived_claims = state.get("survived_claims", [])
    weakened_claims = state.get("weakened_claims", [])
    refuted_claims = state.get("refuted_claims", [])
    verified_claims = state.get("verified_claims", [])
    unverified_claims = state.get("unverified_claims", [])
    freshness_results = state.get("freshness_results", [])
    consistency_score = state.get("consistency_score", 1.0)

    total_claims = len(claims)
    verified_count = len(verified_claims)
    refuted_count = len(refuted_claims)
    weakened_count = len(weakened_claims)
    survived_count = len(survived_claims)

    # Verifizierungsrate (Vera)
    verification_rate = verified_count / total_claims if total_claims > 0 else 0.0

    # Überlebensrate nach Conrad (bezogen auf verifizierte Claims)
    if verified_count > 0:
        survival_rate = survived_count / verified_count
    else:
        survival_rate = 0.0

    # Aktualitätsübersicht (Pia)
    freshness_counts = Counter(r.get("freshness", "fresh") for r in freshness_results)
    freshness_total = len(freshness_results) or 1
    freshness_score = (
        freshness_counts.get("fresh", 0) * 1.0
        + freshness_counts.get("stale", 0) * 0.6
        + freshness_counts.get("expiring", 0) * 0.4
        + freshness_counts.get("outdated", 0) * 0.0
    ) / freshness_total

    # Claims nach Kategorie aufschlüsseln
    claims_by_category = Counter(c.get("category", "UNBEKANNT") for c in claims)

    # Gesamtscore berechnen (gewichteter Durchschnitt)
    overall_score = (
        verification_rate * 0.4
        + survival_rate * 0.3
        + consistency_score * 0.2
        + freshness_score * 0.1
    )

    return {
        "timestamp": datetime.now().isoformat(),
        "total_claims": total_claims,
        "verified_count": verified_count,
        "unverified_count": len(unverified_claims),
        "survived_count": survived_count,
        "weakened_count": weakened_count,
        "refuted_count": refuted_count,
        "consistency_score": round(consistency_score, 4),
        "freshness_summary": {
            "fresh": freshness_counts.get("fresh", 0),
            "stale": freshness_counts.get("stale", 0),
            "outdated": freshness_counts.get("outdated", 0),
            "expiring": freshness_counts.get("expiring", 0),
        },
        "claims_by_category": dict(claims_by_category),
        "overall_score": round(overall_score, 4),
    }


def create_improvement_report(state: dict) -> dict:
    """
    Erstellt den Verbesserungsbericht nach Abschluss der Verbesserungsphase.

    Fasst die Vorschläge aller Verbesserungsagenten zusammen:
    - Rechtliche Aktualisierungen von Lena
    - Sprachliche Verbesserungen von David
    - UX-Probleme von Uma
    - Priorisierte Handlungsempfehlungen (nach Schweregrad sortiert)

    Schweregrad-Reihenfolge für priority_actions:
    critical → major → minor → none
    """
    legal_updates = state.get("legal_updates", [])
    text_improvements = state.get("text_improvements", [])
    ux_issues = state.get("ux_issues", [])

    # Alle Maßnahmen nach Schweregrad sortieren
    severity_order = {"critical": 0, "major": 1, "minor": 2, "none": 3}

    priority_actions = []

    for update in legal_updates:
        severity = update.get("severity", "minor")
        priority_actions.append({
            "source": "Lena (LEGAL)",
            "claim_id": update.get("claim_id", ""),
            "action": update.get("suggested_text", ""),
            "severity": severity,
            "change_type": update.get("change_type", "update"),
        })

    for improvement in text_improvements:
        priority_actions.append({
            "source": "David (DRAFT)",
            "claim_id": improvement.get("claim_id", ""),
            "action": improvement.get("summary", ""),
            "severity": "minor",
            "change_type": "style",
        })

    for issue in ux_issues:
        # Uma verwendet eigene Schweregrad-Bezeichnungen, hier normalisieren
        raw_severity = issue.get("severity", "minor")
        severity_map = {
            "kritisch": "critical",
            "problematisch": "major",
            "verbesserungswürdig": "minor",
            "gut": "none",
        }
        severity = severity_map.get(raw_severity, raw_severity)
        priority_actions.append({
            "source": "Uma (UX)",
            "claim_id": "",
            "action": issue.get("suggestion", ""),
            "severity": severity,
            "section": issue.get("section", ""),
        })

    priority_actions.sort(key=lambda x: severity_order.get(x["severity"], 3))

    return {
        "timestamp": datetime.now().isoformat(),
        "legal_updates": legal_updates,
        "text_improvements": text_improvements,
        "ux_issues": ux_issues,
        "priority_actions": priority_actions,
        "summary": {
            "total_legal_updates": len(legal_updates),
            "total_text_improvements": len(text_improvements),
            "total_ux_issues": len(ux_issues),
            "total_actions": len(priority_actions),
        },
    }
