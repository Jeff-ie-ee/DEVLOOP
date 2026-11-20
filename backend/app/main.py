
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.core.config import settings
from app.core.db_check import check_database_connection

app = FastAPI(
    title=settings.APP_NAME,
    description="Developer Engineering and Intelligence Platform",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)


# Frontend cross-origin configuration.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register application routers.
app.include_router(auth_router)
app.include_router(admin_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to DEVLOOP API",
        "status": "running",
        "version": settings.APP_VERSION,
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
    }


@app.get("/health/database")
def database_health():
    connected = check_database_connection()

    return {
        "status": "connected" if connected else "disconnected",
        "database": "PostgreSQL",
    }
