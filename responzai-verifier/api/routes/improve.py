from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any

from api.security import limiter, require_api_key

router = APIRouter()


class ImproveRequest(BaseModel):
    text: str
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def _build_improve_state(text: str) -> dict:
    """Build minimal PipelineState for the improvement pipeline."""
    return {
        "source_url": "",
        "source_text": text,
        "claims": [],
        "verified_claims": [],
        "unverified_claims": [],
        "survived_claims": [],
        "weakened_claims": [],
        "refuted_claims": [],
        "contradictions": [],
        "consistency_score": 1.0,
        "freshness_results": [],
        "legal_updates": [],
        "text_improvements": [],
        "ux_issues": [],
        "verification_report": None,
        "improvement_report": None,
    }


@router.post("/improve")
@limiter.limit("5/minute")
async def improve_content(request: Request, body: ImproveRequest, _: str = Depends(require_api_key)):
    """
    Verbessert einen Text sprachlich und strukturell.

    Durchläuft die Verbesserungsagenten:
    David (DRAFT) → Uma (UX)

    David prüft Stil, Satzbau und Sprache nach dem responzai-Stilguide.
    Uma analysiert Struktur und Bedienungsfreundlichkeit.

    Hinweis: Lena (LEGAL) ist hier nicht aktiv – für rechtliche Korrektheit
    zuerst /verify aufrufen (die vollständige Pipeline enthält Lena).
    """
    try:
        from pipeline.orchestrator import build_improvement_pipeline

        pipeline = build_improvement_pipeline()
        initial_state = _build_improve_state(body.text)
        result = await pipeline.ainvoke(initial_state)

        report = result.get("improvement_report") or {}

        return {
            "status": "completed",
            "source": body.source or "text",
            "improvement_report": report,
            "summary": report.get("summary", {}),
            "priority_actions": report.get("priority_actions", []),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Improvement pipeline error: {str(e)}")


@router.post("/improve/mock")
async def improve_mock(request: Request, body: ImproveRequest):
    """
    Mock-Endpunkt fuer Dashboard-Tests. Gibt realistische Fake-Daten zurueck,
    ohne die Claude API aufzurufen. Kein API-Key erforderlich.
    """
    return {
        "status": "completed",
        "source": body.source or "mock",
        "improvement_report": {
            "text_improvements": [
                {"original": "KI-Systeme, die in der EU eingesetzt werden, muessen einer Konformitaetsbewertung unterzogen werden.", "suggestion": "Hochriskante KI-Systeme in der EU benoetigen eine Konformitaetsbewertung."},
                {"original": "Das Compliance-Framework muss implementiert werden.", "suggestion": "Der Rechtsrahmen muss umgesetzt werden."},
            ],
            "ux_issues": [
                {"issue": "Kein klarer Einstieg fuer die Zielgruppe (KMU ohne KI-Vorwissen).", "severity": "problematisch"},
                {"issue": "Durchschnittliche Satzlaenge: 28 Woerter (Empfehlung: max. 20).", "severity": "verbesserungswuerdig"},
            ],
            "priority_actions": [
                {"source": "David (DRAFT)", "action": "Schachtelkonstruktionen aufloesen fuer bessere Lesbarkeit.", "severity": "major"},
                {"source": "Uma (UX)", "action": "Einstieg fuer KMU-Zielgruppe optimieren – mit konkreter Handlungsempfehlung beginnen.", "severity": "major"},
                {"source": "David (DRAFT)", "action": "Anglizismen durch deutsche Fachbegriffe ersetzen.", "severity": "minor"},
                {"source": "Uma (UX)", "action": "Durchschnittliche Satzlaenge auf max. 20 Woerter reduzieren.", "severity": "minor"},
            ],
        },
        "summary": {
            "total_issues": 4,
            "style_issues": 2,
            "ux_issues": 2,
            "overall_quality": "gut",
            "recommended_action": "kleinere Verbesserungen empfohlen",
        },
        "priority_actions": [
            {"source": "David (DRAFT)", "action": "Schachtelkonstruktionen aufloesen fuer bessere Lesbarkeit.", "severity": "major"},
            {"source": "Uma (UX)", "action": "Einstieg fuer KMU-Zielgruppe optimieren – mit konkreter Handlungsempfehlung beginnen.", "severity": "major"},
            {"source": "David (DRAFT)", "action": "Anglizismen durch deutsche Fachbegriffe ersetzen.", "severity": "minor"},
            {"source": "Uma (UX)", "action": "Durchschnittliche Satzlaenge auf max. 20 Woerter reduzieren.", "severity": "minor"},
        ],
    }
