from fastapi import APIRouter
from app.api.v1.endpoints import validation

api_router = APIRouter()
api_router.include_router(validation.router, tags=["validation"])
