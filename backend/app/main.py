"""FastAPI application entry point"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    accounts_router,
    activation_router,
    auth_router,
    booking_router,
    documents_router,
    journey_router,
    offers_router,
    signature_router,
    simulations_router,
    verifications_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events - startup and shutdown"""
    # Startup: Run seed data
    print("🚀 Starting Ruralvía Pre-Approved Loan Platform...")
    try:
        from app.seed import run_seed
        run_seed()
        print("✅ Seed data loaded successfully")
    except Exception as e:
        print(f"⚠️  Seed data loading failed: {e}")

    # Start reconciliation worker
    from app.workers.reconciliation_worker import (
        start_reconciliation_worker,
        stop_reconciliation_worker,
    )
    worker_task = asyncio.create_task(start_reconciliation_worker(poll_interval_seconds=30, max_retries=10))
    print("✅ Reconciliation worker started")

    yield

    # Shutdown: Stop reconciliation worker
    print("🛑 Shutting down reconciliation worker...")
    await stop_reconciliation_worker()
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    print("🛑 Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title="Ruralvía Pre-Approved Loan Platform API",
    description="Backend API for pre-approved consumer loan origination",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint - health check"""
    return {
        "service": "Ruralvía Pre-Approved Loan Platform",
        "status": "operational",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy"}


# Register API routers
# Note: Routers now include full paths including /api/v1 prefix
# Auth router still uses /api/v1 prefix pattern
app.include_router(auth_router, prefix="/api/v1")
# Journey-scoped routers now contain full paths in their route definitions
app.include_router(offers_router)
app.include_router(simulations_router)
app.include_router(accounts_router)
app.include_router(documents_router)
app.include_router(verifications_router)
app.include_router(signature_router)
app.include_router(booking_router)
app.include_router(activation_router)
app.include_router(journey_router, prefix="/api/v1")
