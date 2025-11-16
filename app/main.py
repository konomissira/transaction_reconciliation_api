from fastapi import FastAPI
from app.database import engine, Base
from app.api.endpoints import router

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Transaction Reconciliation API",
    description="API for reconciling transactions between different systems using set operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include API router
app.include_router(router)


@app.get("/")
def read_root():
    """Root endpoint - health check"""
    return {
        "message": "Transaction Reconciliation API",
        "status": "running",
        "version": "1.0.0",
        "docs": "Visit /docs for API documentation"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}