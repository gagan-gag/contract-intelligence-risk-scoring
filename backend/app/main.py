from fastapi import FastAPI

app = FastAPI(
    title="Contract Intelligence API",
    version="0.1.0",
    description="API for contract ingestion, analysis, and risk scoring.",
)

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