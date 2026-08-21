from fastapi import FastAPI

from backend.app.routers.search import router as search_router

app = FastAPI(
    title="Contract Intelligence API",
    version="0.1.0",
    description="API for contract ingestion, analysis, and risk scoring.",
)

app.include_router(search_router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return service status for local, CI, and deployment checks."""
    return {"status": "ok"}