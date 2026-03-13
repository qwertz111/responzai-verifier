from fastapi import APIRouter

router = APIRouter()


@router.post("/verify")
async def verify_content(url: str = None, text: str = None, mode: str = "full"):
    """Startet einen Prüflauf für eine URL oder einen Text."""
    # TODO: Pipeline-Integration (Phase 4)
    return {"status": "not_implemented"}
