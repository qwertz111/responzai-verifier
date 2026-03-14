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
