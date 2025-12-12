"""
Sally Love Real Estate Voice Agent System
FastAPI application entry point
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from src.config.settings import settings
from src.utils.logger import setup_logger, get_logger
from src.utils.errors import VapiError, IntegrationError

# Import function handlers
from src.functions.check_property import router as check_property_router
from src.functions.get_agent_info import router as get_agent_info_router
from src.functions.route_to_agent import router as route_to_agent_router
from src.functions.create_buyer_lead import router as create_buyer_lead_router
from src.functions.create_seller_lead import router as create_seller_lead_router
from src.functions.send_notification import router as send_notification_router

# Import webhook handlers
from src.webhooks.vapi_webhooks import router as vapi_webhooks_router
from src.webhooks.crm_webhooks import router as crm_webhooks_router

# Setup logging
setup_logger()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info(f"🚀 Starting Sally Love Voice Agent System v1.0.0")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Server: {settings.HOST}:{settings.PORT}")
    logger.info(f"Business: {settings.BUSINESS_NAME}")
    logger.info(f"Phone: {settings.BUSINESS_PHONE}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Sally Love Voice Agent System")


# Initialize FastAPI app
app = FastAPI(
    title="Sally Love Real Estate Voice Agent API",
    description="AI-powered voice automation system for real estate operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(VapiError)
async def vapi_error_handler(request: Request, exc: VapiError):
    """Handle Vapi-specific errors"""
    logger.error(f"Vapi error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "details": exc.details},
    )


@app.exception_handler(IntegrationError)
async def integration_error_handler(request: Request, exc: IntegrationError):
    """Handle integration errors"""
    logger.error(f"Integration error ({exc.service}): {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "service": exc.service,
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.exception(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)},
    )


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "service": "Sally Love Real Estate Voice Agent",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "Sally Love Real Estate Voice Agent",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "business": settings.BUSINESS_NAME,
        "phone": settings.BUSINESS_PHONE,
        "integrations": {
            "vapi": "configured" if settings.VAPI_API_KEY else "not_configured",
            "boldtrail": "configured" if settings.BOLDTRAIL_API_KEY else "not_configured",
            "stellar_mls": "configured" if settings.STELLAR_MLS_USERNAME else "not_configured",
            "twilio": "configured" if settings.TWILIO_ACCOUNT_SID else "not_configured",
        },
    }


# Include function routers (Vapi tools)
app.include_router(check_property_router, prefix="/functions", tags=["Functions"])
app.include_router(get_agent_info_router, prefix="/functions", tags=["Functions"])
app.include_router(route_to_agent_router, prefix="/functions", tags=["Functions"])
app.include_router(create_buyer_lead_router, prefix="/functions", tags=["Functions"])
app.include_router(create_seller_lead_router, prefix="/functions", tags=["Functions"])
app.include_router(send_notification_router, prefix="/functions", tags=["Functions"])

# Include webhook routers
app.include_router(vapi_webhooks_router, prefix="/webhooks/vapi", tags=["Webhooks"])
app.include_router(crm_webhooks_router, prefix="/webhooks/crm", tags=["Webhooks"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )

