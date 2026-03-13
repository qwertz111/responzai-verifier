from fastapi import APIRouter

router = APIRouter()


@router.get("/reports")
async def list_reports():
    """Gibt eine Liste aller Prüfberichte zurück."""
    # TODO: Datenbank-Abfrage (Phase 1)
    return {"reports": []}


@router.get("/reports/latest")
async def latest_report():
    """Gibt den neuesten Prüfbericht zurück."""
    # TODO: Datenbank-Abfrage (Phase 1)
    return {"status": "no_reports"}
