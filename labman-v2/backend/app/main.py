from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import api_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/")
def root():
    return {
        "message": "Welcome to LabMan API",
        "docs": f"{settings.API_V1_STR}/docs",
        "version": "2.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(api_router, prefix=settings.API_V1_STR)
