from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, model_validator
from typing import Optional, Dict, Any
from datetime import datetime

from api.security import limiter, require_api_key

router = APIRouter()


class VerifyRequest(BaseModel):
    text: str = ""
    url: Optional[str] = None
    source: Optional[str] = None
    mode: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def check_text_or_url(self):
        if not self.text and not self.url:
            raise ValueError("Either 'text' or 'url' must be provided.")
        return self


class DraftRequest(BaseModel):
    text: str = ""
    url: Optional[str] = None
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def check_text_or_url(self):
        if not self.text and not self.url:
            raise ValueError("Either 'text' or 'url' must be provided.")
        return self


def _build_initial_state(text: str, url: str) -> dict:
    """Build the initial PipelineState dict with all required fields."""
    return {
        "source_url": url or "",
        "source_text": text or "",
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


def _derive_verdict(score: float, refuted_count: int) -> str:
    """Derive a human-readable verdict from the overall score."""
    if refuted_count > 0 and score < 0.7:
        return "rejected"
    if score >= 0.9:
        return "verified"
    if score >= 0.7:
        return "partially_verified"
    return "rejected"


def _build_response(result: dict, source: str) -> dict:
    """Build the standardized API response from pipeline results."""
    report = result.get("verification_report") or {}
    score = report.get("overall_score", 0.0)
    refuted = report.get("refuted_count", 0)

    return {
        "status": "completed",
        "source": source,
        "total_claims": report.get("total_claims", 0),
        "verified_claims": report.get("verified_count", 0),
        "issues_found": report.get("refuted_count", 0) + report.get("weakened_count", 0),
        "score": round(score, 4),
        "verdict": _derive_verdict(score, refuted),
        "verification_report": result.get("verification_report"),
        "improvement_report": result.get("improvement_report"),
    }


@router.post("/verify")
@limiter.limit("5/minute")
async def verify_content(request: Request, body: VerifyRequest, _: str = Depends(require_api_key)):
    """
    Startet einen Prueflauf fuer einen Text oder eine URL.

    Durchlaeuft alle 8 Agenten der Pipeline:
    Simon -> Vera -> Conrad -> Sven -> Pia -> Lena -> David -> Uma
    """
    try:
        from pipeline.orchestrator import build_pipeline

        pipeline = build_pipeline()
        initial_state = _build_initial_state(body.text, body.url)
        result = await pipeline.ainvoke(initial_state)

        return _build_response(result, body.source or body.url or "text")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@router.post("/verify/draft")
@limiter.limit("5/minute")
async def verify_draft(request: Request, body: DraftRequest, _: str = Depends(require_api_key)):
    """
    Prueft einen Entwurf auf Publish-Bereitschaft.

    Gleiche Pipeline wie /verify, mit zusaetzlicher Empfehlung:
    - "approved": Score >= 0.9, keine refuted Claims
    - "approved_with_changes": Score >= 0.7
    - "rejected": Score < 0.7 oder kritische Fehler
    """
    try:
        from pipeline.orchestrator import build_pipeline

        pipeline = build_pipeline()
        initial_state = _build_initial_state(body.text, body.url)
        result = await pipeline.ainvoke(initial_state)

        response = _build_response(result, body.source or body.url or "draft")

        # Map verdict to n8n-compatible recommendation
        verdict = response["verdict"]
        if verdict == "verified":
            response["verdict"] = "approved"
        elif verdict == "partially_verified":
            response["verdict"] = "approved_with_changes"
        else:
            response["verdict"] = "rejected"

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@router.get("/verify/{task_id}")
async def get_verify_result(task_id: str):
    """
    Ruft Ergebnis eines Prueflaufs ab (fuer zukuenftige async-Verarbeitung).
    """
    return {"status": "not_implemented"}


@router.get("/health")
async def health_check():
    """Health-Check Endpunkt fuer Load Balancer."""
    return {
        "status": "healthy",
        "version": "1.0.0",
    }
