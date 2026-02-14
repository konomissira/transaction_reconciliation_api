from fastapi import FastAPI
from app.database import engine, Base
from app.api.endpoints import router

# Assistant router
from assistant.router import router as assistant_router

from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
        "null",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)
app.include_router(assistant_router, prefix="/assistant", tags=["assistant"])


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