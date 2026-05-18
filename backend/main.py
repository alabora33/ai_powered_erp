"""
FastAPI main application entry point.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from backend.config import settings
from backend.database import check_db_connection, create_tables
from backend.routers.analytics import router as analytics_router
from backend.routers.templates import router as templates_router
from backend.routers.upload import router as upload_router

# ─── Lifespan ─────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 Starting AI ERP API...")

    # Create upload directory
    os.makedirs(settings.upload_dir, exist_ok=True)

    # Create database tables
    try:
        await create_tables()
    except Exception as e:
        logger.error(f"DB init error: {e}")

    logger.info(f"✅ AI ERP API ready! Environment: {settings.environment}")
    yield
    logger.info("👋 Shutting down AI ERP API...")


# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI ERP – Excel Data Mapper",
    description="""
## AI-Powered ERP Data Mapping System

Upload Excel, CSV, or ERP export files and let AI automatically:
- **Detect** column meanings in Turkish and English
- **Map** them to a standard emission/consumption schema  
- **Validate** data quality and report errors
- **Export** clean, structured data as CSV or JSON

### Key Features
- 🤖 Gemini AI column analysis with structured output
- 📊 Support for Excel (.xlsx, .xls) and CSV files
- ⚡ Async background processing with Celery
- 📈 Real-time progress tracking
- 🔍 Data quality scoring
    """,
    version=settings.app_version,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ─── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(templates_router)
app.include_router(upload_router)
app.include_router(analytics_router)

# ─── Health Check ─────────────────────────────────────────────────────────────


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
async def health_check():
    """System health check endpoint."""
    db_ok = await check_db_connection()

    # Check Redis
    redis_ok = False
    try:
        import redis

        r = redis.from_url(settings.redis_url, socket_timeout=2)
        r.ping()
        redis_ok = True
    except Exception:
        pass

    # Check AI service
    ai_ok = bool(settings.gemini_api_key)

    all_ok = db_ok and redis_ok and ai_ok
    return JSONResponse(
        status_code=200 if all_ok else 503,
        content={
            "status": "healthy" if all_ok else "degraded",
            "database": "connected" if db_ok else "disconnected",
            "redis": "connected" if redis_ok else "disconnected",
            "ai_service": "configured" if ai_ok else "not configured",
            "version": settings.app_version,
            "environment": settings.environment,
        },
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/api/docs",
        "health": "/health",
    }
