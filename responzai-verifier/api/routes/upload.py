# api/routes/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from document_ingestion.router import ingest_document
from document_ingestion.storage import save_upload
from pipeline.orchestrator import build_pipeline
from api.security import require_api_key
from api.monitoring import log_pipeline_start, log_pipeline_success, log_pipeline_error

router = APIRouter()

@router.post("/verify/document")
async def verify_document(
    file: UploadFile = File(...),
    mode: str = "full",
    _: str = Depends(require_api_key)
):
    """
    Nimmt eine Datei entgegen, extrahiert den Text und
    startet die Prüfpipeline.

    Ablauf:
    1. Datei sicher speichern
    2. Format erkennen und Text extrahieren
    3. Text an die Prüfpipeline übergeben
    4. Ergebnis zurückgeben

    Parameter:
    - file: Die hochgeladene Datei (beliebiges unterstütztes Format)
    - mode: "full" (alle 8 Agenten) oder "quick" (nur Simon + Vera)

    Beispiel mit curl:
    curl -X POST "https://api.responzai.eu/verify/document" \
         -F "file=@mein_dokument.pdf" \
         -F "mode=full"
    """
    # Schritt 1: Datei speichern
    content = await file.read()
    try:
        stored = await save_upload(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Schritt 2: Text extrahieren
    try:
        document = await ingest_document(
            stored["stored_path"],
            file.filename,
            file.content_type
        )
    except ValueError as e:
        raise HTTPException(status_code=415, detail=str(e))

    # Schritt 3: Pipeline starten
    log_pipeline_start()
    pipeline = build_pipeline()

    initial_state = {
        "source_url": f"upload://{file.filename}",
        "source_text": document["text"],
        "claims": [],
        "verified_claims": [],
        "unverified_claims": [],
        "survived_claims": [],
        "weakened_claims": [],
        "refuted_claims": [],
        "contradictions": [],
        "consistency_score": 0.0,
        "freshness_results": [],
        "legal_updates": [],
        "text_improvements": [],
        "ux_issues": [],
        "verification_report": None,
        "improvement_report": None,
    }

    try:
        result = await pipeline.ainvoke(initial_state)
        log_pipeline_success()
    except Exception as e:
        log_pipeline_error("verify/document", e, {"filename": file.filename})
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    return {
        "filename": file.filename,
        "format": document["format"],
        "pages": document["pages"],
        "text_length": document["cleaned_length"],
        "metadata": document["metadata"],
        "total_claims": len(result["claims"]),
        "verified_claims": len(result["verified_claims"]),
        "issues_found": len(result["refuted_claims"]) + len(result["weakened_claims"]),
        "verification_report": result["verification_report"],
    }
