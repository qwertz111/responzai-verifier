from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from api.security import limiter

app = FastAPI(
    title="responzai Verifier API",
    description="Multi-Agent Verification System fuer responzai",
    version="1.0.0"
)

# Rate Limiter registrieren
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS: nur responzai.eu und localhost fuer lokale Entwicklung
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://responzai.eu",
        "https://www.responzai.eu",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
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
