from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, model_validator
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio
import json

from api.security import limiter, require_api_key
from api.monitoring import log_pipeline_start, log_pipeline_success, log_pipeline_error

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
    Simon -> Vera -> Conrad -> Sven -> Pia -> Lena -> Davina -> Uma
    """
    log_pipeline_start()
    try:
        from pipeline.orchestrator import build_pipeline

        pipeline = build_pipeline()
        initial_state = _build_initial_state(body.text, body.url)
        result = await pipeline.ainvoke(initial_state)

        log_pipeline_success()
        return _build_response(result, body.source or body.url or "text")

    except Exception as e:
        log_pipeline_error("verify", e, {"source": body.source or body.url or "text"})
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
    log_pipeline_start()
    try:
        from pipeline.orchestrator import build_pipeline

        pipeline = build_pipeline()
        initial_state = _build_initial_state(body.text, body.url)
        result = await pipeline.ainvoke(initial_state)

        log_pipeline_success()
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
        log_pipeline_error("verify/draft", e, {"source": body.source or body.url or "draft"})
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@router.post("/verify/mock")
async def verify_mock(request: Request, body: VerifyRequest):
    """
    Mock-Endpunkt fuer Dashboard-Tests. Gibt realistische Fake-Daten zurueck,
    ohne die Claude API aufzurufen. Kein API-Key erforderlich.
    """
    return {
        "status": "completed",
        "source": body.source or body.url or "mock",
        "total_claims": 6,
        "verified_claims": 4,
        "issues_found": 2,
        "score": 0.82,
        "verdict": "partially_verified",
        "verification_report": {
            "overall_score": 0.82,
            "total_claims": 6,
            "verified_count": 4,
            "unverified_count": 1,
            "survived_count": 3,
            "weakened_count": 1,
            "refuted_count": 1,
            "claims_by_category": {
                "LEGAL_CLAIM": 4,
                "MARKET_CLAIM": 1,
                "PRODUCT_CLAIM": 1,
            },
            "consistency_score": 0.88,
            "freshness_summary": {
                "fresh": 5,
                "stale": 1,
                "outdated": 0,
            },
        },
        "improvement_report": {
            "legal_updates": [
                {"claim_id": "claim_006", "update": "EU-KI-Haftungsrichtlinie 2024 widerlegt diese Aussage ausdruecklich."},
            ],
            "text_improvements": [
                {"original": "KI-Systeme, die als hochriskant eingestuft sind, muessen einer Pruefung unterzogen werden.", "suggestion": "Hochriskante KI-Systeme muessen eine Konformitaetsbewertung durchlaufen."},
            ],
            "ux_issues": [
                {"issue": "Kein klarer Call-to-Action fuer KMU-Zielgruppe sichtbar.", "severity": "problematisch"},
                {"issue": "Durchschnittliche Satzlaenge ueberschreitet 20 Woerter.", "severity": "verbesserungswuerdig"},
            ],
            "priority_actions": [
                {"source": "Conrad (CONTRA)", "action": "claim_006 entfernen oder korrigieren: KI-Haftung ist rechtlich verankert.", "severity": "critical"},
                {"source": "Vera (VERIFY)", "action": "Marktanteil-Angabe (80 %) auf belegbare Quelle anpassen (Eurostat: 25 %).", "severity": "major"},
                {"source": "Davina (DRAFT)", "action": "Schachtelkonstruktion in Satz 3 aufloesen.", "severity": "minor"},
            ],
        },
    }


@router.get("/verify/{task_id}")
async def get_verify_result(task_id: str):
    """
    Ruft Ergebnis eines Prueflaufs ab (fuer zukuenftige async-Verarbeitung).
    """
    return {"status": "not_implemented"}


@router.get("/health")
async def health_check():
    """Erweiterter Health-Check: API + Datenbank + Pipeline-Stats."""
    from api.monitoring import get_stats

    stats = get_stats()
    db_ok = False
    try:
        from database.connection import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        db_ok = True
    except Exception:
        pass

    status = "healthy" if db_ok else "degraded"
    return {
        "status": status,
        "version": "1.0.0",
        "database": "connected" if db_ok else "disconnected",
        "uptime": stats["uptime_human"],
        "pipeline": stats["pipeline_runs"],
    }


@router.get("/admin/errors")
async def get_pipeline_errors(_: str = Depends(require_api_key)):
    """Gibt die letzten Pipeline-Fehler zurueck (API-Key geschuetzt)."""
    from api.monitoring import get_errors, get_stats

    return {
        "stats": get_stats(),
        "errors": get_errors(limit=20),
    }


@router.post("/verify/stream")
@limiter.limit("5/minute")
async def verify_stream(request: Request, body: VerifyRequest, _: str = Depends(require_api_key)):
    """SSE-Streaming endpoint. Sendet Echtzeit-Events waehrend der Pipeline laeuft."""
    from pipeline.orchestrator import build_pipeline
    from pipeline.events import PipelineEventBus

    bus = PipelineEventBus()
    initial_state = _build_initial_state(body.text, body.url)
    initial_state["_event_bus"] = bus

    async def run_pipeline():
        try:
            log_pipeline_start()
            await bus.emit("pipeline_start", {
                "agents": ["simon", "vera", "conrad", "sven", "pia", "lena", "david", "uma"],
                "total_agents": 8,
            })
            pipeline = build_pipeline()
            result = await pipeline.ainvoke(initial_state)
            log_pipeline_success()

            response_data = _build_response(result, body.source or body.url or "text")
            await bus.emit("pipeline_complete", {"result": response_data})
        except Exception as e:
            log_pipeline_error("verify/stream", e, {})
            await bus.emit("error", {"message": str(e)})
        finally:
            await bus.finish()

    asyncio.ensure_future(run_pipeline())

    return StreamingResponse(
        bus.stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/verify/stream/mock")
async def verify_stream_mock(request: Request, body: VerifyRequest):
    """Mock SSE-Stream fuer Dashboard-Entwicklung ohne API-Kosten."""
    from pipeline.events import PipelineEventBus

    bus = PipelineEventBus()

    async def mock_pipeline():
        agents = [
            ("simon", "Simon", "SCOUT", "Extrahiert pruefbare Behauptungen", 1.0,
             "12 Claims gefunden", {"claims": 12}),
            ("vera", "Vera", "VERIFY", "Prueft 12 Claims gegen die Wissensbasis", 2.0,
             "8 verifiziert, 4 unsicher", {"verified": 8, "unverified": 4}),
            ("conrad", "Conrad", "CONTRA", "Prueft 8 verifizierte Claims adversarial", 1.5,
             "6 ueberlebt, 1 geschwaecht, 1 widerlegt", {"survived": 6, "weakened": 1, "refuted": 1}),
            ("sven", "Sven", "SYNC", "Prueft 7 Claims auf Widersprueche", 1.0,
             "Keine Widersprueche gefunden", {"contradictions": 0, "consistency_score": 1.0}),
            ("pia", "Pia", "PULSE", "Prueft 7 Claims auf Aktualitaet", 0.5,
             "7 Claims geprueft", {"checked": 7}),
            ("lena", "Lena", "LEGAL", "Erstellt rechtliche Updates", 1.5,
             "2 rechtliche Updates", {"updates": 2}),
            ("david", "Davina", "DRAFT", "Optimiert den Text sprachlich", 1.5,
             "5 Textverbesserungen", {"improvements": 5}),
            ("uma", "Uma", "UX", "Analysiert Bedienungsfreundlichkeit", 1.5,
             "4 UX-Probleme", {"issues": 4}),
        ]

        await bus.emit("pipeline_start", {
            "agents": [a[0] for a in agents],
            "total_agents": len(agents),
        })

        for agent_id, name, role, desc, duration, summary, stats in agents:
            await bus.emit("agent_start", {
                "agent": agent_id, "name": name, "role": role, "description": desc,
            })
            # Simulate progress steps
            steps = 3
            for step in range(1, steps + 1):
                await asyncio.sleep(duration / steps)
                await bus.emit("agent_progress", {
                    "agent": agent_id,
                    "message": f"Schritt {step}/{steps}...",
                    "progress": step / steps,
                })
            await bus.emit("agent_complete", {
                "agent": agent_id, "summary": summary, "stats": stats,
            })

        # Send mock final result
        mock_result = {
            "status": "completed", "source": body.source or "mock",
            "total_claims": 12, "verified_claims": 8, "issues_found": 2,
            "score": 0.82, "verdict": "partially_verified",
            "verification_report": {
                "overall_score": 0.82, "total_claims": 12,
                "verified_count": 8, "unverified_count": 4,
                "survived_count": 6, "weakened_count": 1, "refuted_count": 1,
                "consistency_score": 1.0,
                "freshness_summary": {"fresh": 7, "stale": 0, "outdated": 0, "expiring": 0},
                "claims_by_category": {"LEGAL_CLAIM": 7, "PRODUCT_CLAIM": 3, "MARKET_CLAIM": 2},
                "claims_detail": [],
            },
            "improvement_report": {
                "legal_updates": [], "text_improvements": [],
                "ux_issues": [], "priority_actions": [],
                "summary": {"total_legal_updates": 0, "total_text_improvements": 5,
                            "total_ux_issues": 4, "total_actions": 9},
            },
        }
        await bus.emit("pipeline_complete", {"result": mock_result})
        await bus.finish()

    asyncio.ensure_future(mock_pipeline())

    return StreamingResponse(
        bus.stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
