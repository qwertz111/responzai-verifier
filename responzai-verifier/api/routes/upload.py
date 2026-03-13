# api/routes/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from document_ingestion.router import ingest_document
from document_ingestion.storage import save_upload
from pipeline.orchestrator import build_pipeline

router = APIRouter()

@router.post("/verify/document")
async def verify_document(
    file: UploadFile = File(...),
    mode: str = "full"
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

    result = await pipeline.ainvoke(initial_state)

    return {
        "filename": file.filename,
        "format": document["format"],
        "pages": document["pages"],
        "text_length": document["cleaned_length"],
        "metadata": document["metadata"],
        "total_claims": len(result["claims"]),
        "verified_claims": len(result["verified_claims"]),
        "issues_found": len(result["refuted_claims"]) + len(result["weakened_claims"]),
        "report": result["verification_report"],
    }
