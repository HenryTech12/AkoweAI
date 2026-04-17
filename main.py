"""Main FastAPI application for AkoweAI backend."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from config import settings
from model.database import init_db
from exceptions import setup_exception_handlers
from routers import webhooks, transactions, reports, users, health
import logging
import logging.config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Multilingual AI Financial Bridge for Africa's Invisible MSMEs",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # In production, specify allowed hosts
)


# Setup exception handlers
setup_exception_handlers(app)


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


# Include routers
app.include_router(webhooks.router)
app.include_router(transactions.router, prefix=settings.api_v1_str)
app.include_router(reports.router, prefix=settings.api_v1_str)
app.include_router(users.router, prefix=settings.api_v1_str)
app.include_router(users.users_router, prefix=settings.api_v1_str)
app.include_router(health.router, prefix=settings.api_v1_str)


# Root endpoint
@app.get("/", tags=["info"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "description": "Multilingual AI Financial Bridge for Africa's Invisible MSMEs",
        "docs_url": "/docs",
        "health_url": f"{settings.api_v1_str}/health"
    }


# API version endpoint
@app.get(f"{settings.api_v1_str}/", tags=["info"])
async def api_info():
    """API v1 information."""
    return {
        "version": "1.0.0",
        "endpoints": {
            "auth": f"{settings.api_v1_str}/auth",
            "transactions": f"{settings.api_v1_str}/transactions",
            "reports": f"{settings.api_v1_str}/reports",
            "users": f"{settings.api_v1_str}/users",
            "health": f"{settings.api_v1_str}/health"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
