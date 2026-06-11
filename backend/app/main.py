from fastapi import FastAPI

from app.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Backend API for Asset Servicing AI Copilot project",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} is running",
        "environment": settings.app_env,
        "status": "ok",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "backend",
        "environment": settings.app_env,
    }