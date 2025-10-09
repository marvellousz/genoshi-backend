from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api.v1.api import api_router
from app.models.schemas import HealthResponse

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="Insurance document validation API",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["root"])
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "active",
        "endpoints": {
            "health": "/health",
            "validate": "/api/v1/validate",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    return HealthResponse(
        status="healthy",
        service="insurance-validator",
        version=settings.app_version
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
