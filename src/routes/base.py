from fastapi import FastAPI, APIRouter
import os

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
    responses={404: {"description": "Not found"}},
)

@base_router.get("/")
async def welcome():
    app_name = os.getenv("APP_NAME", "mini-rag")
    app_version = os.getenv("APP_VERSION", "1.0.0")
    return {
        "app_name": app_name,
        "app_version": app_version,
    }