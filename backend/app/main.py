from fastapi import FastAPI

try:
    from .routers.risk import router as risk_router
except ImportError:  # pragma: no cover - support script execution
    # Pylance may not resolve the package when the app is executed as a script.
    from app.routers.risk import router as risk_router  # type: ignore[import-not-found]

app = FastAPI(
    title="Contract Intelligence API",
    version="0.1.0",
    description="API for contract ingestion, analysis, and risk scoring.",
)
app.include_router(risk_router)

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