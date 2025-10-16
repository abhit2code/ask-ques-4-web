from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import ingest, query
from src.database.connection import create_tables

# Create FastAPI app
app = FastAPI(
    title="RAG Engine API",
    description="Scalable Web-Aware RAG Engine",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest.router, prefix="/api", tags=["ingestion"])
app.include_router(query.router, prefix="/api", tags=["query"])

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    create_tables()

@app.get("/")
async def root():
    return {"message": "RAG Engine API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
