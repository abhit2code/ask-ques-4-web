from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from src.api.dependencies import get_db
from src.models.ingestion import URLIngestion
from src.workers.tasks import process_url_task
import validators

router = APIRouter()

class URLIngestRequest(BaseModel):
    url: HttpUrl

class URLIngestResponse(BaseModel):
    message: str
    url: str
    status: str

@router.post("/ingest-url", response_model=URLIngestResponse)
async def ingest_url(request: URLIngestRequest, db: Session = Depends(get_db)):
    """Submit URL for processing"""
    url = str(request.url)
    
    # Validate URL
    if not validators.url(url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Check if URL already exists
    existing_url = db.query(URLIngestion).filter(URLIngestion.url == url).first()
    if existing_url:
        if existing_url.status == "completed":
            return URLIngestResponse(
                message="URL already processed",
                url=url,
                status=existing_url.status
            )
        elif existing_url.status == "processing":
            return URLIngestResponse(
                message="URL is currently being processed",
                url=url,
                status=existing_url.status
            )
    
    # Create or update URL record
    if existing_url:
        existing_url.status = "pending"
        db.commit()
    else:
        url_record = URLIngestion(url=url, status="pending")
        db.add(url_record)
        db.commit()
    
    # Queue processing task
    try:
        process_url_task.delay(url)
        return URLIngestResponse(
            message="URL queued for processing",
            url=url,
            status="pending"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue URL: {str(e)}")

@router.get("/status")
async def get_overall_status(db: Session = Depends(get_db)):
    """Get overall ingestion status"""
    from sqlalchemy import func
    
    # Count URLs by status
    status_counts = db.query(
        URLIngestion.status,
        func.count(URLIngestion.id).label('count')
    ).group_by(URLIngestion.status).all()
    
    # Convert to dictionary
    status_dict = {status: count for status, count in status_counts}
    
    return {
        "pending_urls": status_dict.get("pending", 0),
        "processing_urls": status_dict.get("processing", 0),
        "completed_urls": status_dict.get("completed", 0),
        "failed_urls": status_dict.get("failed", 0),
        "total_urls": sum(status_dict.values())
    }

@router.get("/status/{url_id}")
async def get_ingestion_status(url_id: int, db: Session = Depends(get_db)):
    """Get ingestion status for a URL"""
    url_record = db.query(URLIngestion).filter(URLIngestion.id == url_id).first()
    if not url_record:
        raise HTTPException(status_code=404, detail="URL not found")
    
    return {
        "id": url_record.id,
        "url": url_record.url,
        "status": url_record.status,
        "created_at": url_record.created_at,
        "updated_at": url_record.updated_at,
        "error_message": url_record.error_message
    }
