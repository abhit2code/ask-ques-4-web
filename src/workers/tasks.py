import asyncio
import hashlib
from sqlalchemy.orm import Session
from src.workers.celery_app import celery_app
from src.services.scraper import ContentProcessor
from src.services.vector_store import VectorStore
from src.database.connection import SessionLocal
from src.models.ingestion import URLIngestion

@celery_app.task(bind=True)
def process_url_task(self, url: str):
    """Celery task to process URL content"""
    
    # Use default database connection
    db = SessionLocal()
    try:
        url_record = db.query(URLIngestion).filter(URLIngestion.url == url).first()
        if url_record:
            url_record.status = "processing"
            db.commit()
        
        # Process the URL
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_process_url_async(url, db))
            return result
        finally:
            loop.close()
            
    except Exception as e:
        # Update status to failed
        if url_record:
            url_record.status = "failed"
            url_record.error_message = str(e)
            db.commit()
        raise
    finally:
        db.close()

async def _process_url_async(url: str, db: Session):
    """Async function to process URL"""
    processor = ContentProcessor()
    vector_store = VectorStore()
    
    try:
        # Fetch content
        content = await processor.fetch_content(url)
        
        if not content or len(content.strip()) < 100:
            raise Exception("Content too short or empty")
        
        # Create content hash
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Chunk content
        documents = processor.chunk_content(content, url)
        
        if not documents:
            raise Exception("No valid chunks created")
        
        # Store in vector database
        vector_store.add_documents(documents)
        
        # Update database record
        url_record = db.query(URLIngestion).filter(URLIngestion.url == url).first()
        if url_record:
            url_record.status = "completed"
            url_record.content_hash = content_hash
            db.commit()
        
        return {
            "status": "completed",
            "chunks_created": len(documents),
            "content_hash": content_hash
        }
        
    except Exception as e:
        # Update status to failed
        url_record = db.query(URLIngestion).filter(URLIngestion.url == url).first()
        if url_record:
            url_record.status = "failed"
            url_record.error_message = str(e)
            db.commit()
        raise
