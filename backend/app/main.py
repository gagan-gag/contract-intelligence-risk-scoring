from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.risk import router as risk_router
from app.routers.search import router as search_router
from app.routers.upload import router as upload_router

app = FastAPI(
    title="Contract Intelligence API",
    version="0.1.0",
    description="API for contract ingestion, analysis, and risk scoring.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(risk_router)
app.include_router(search_router)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "message": "Contract Intelligence API",
        "status": "running",
    }


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return service status for local, CI, and deployment checks."""
    return {"status": "ok"}