from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="responzai Verifier API",
    description="Multi-Agent Verification System für responzai",
    version="1.0.0"
)

# CORS erlauben (damit die Website auf die API zugreifen kann)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://responzai.eu"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Routes einbinden
from api.routes.verify import router as verify_router
from api.routes.upload import router as upload_router
from api.routes.improve import router as improve_router
from api.routes.reports import router as reports_router

app.include_router(verify_router)
app.include_router(upload_router)
app.include_router(improve_router)
app.include_router(reports_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
