import asyncio
import hashlib
from sqlalchemy.orm import Session
from src.workers.celery_app import celery_app
from src.services.scraper import ContentProcessor
from src.services.vector_store import VectorStore
from src.database.connection import SessionLocal
from src.models.ingestion import URLIngestion

@celery_app.task(bind=True)
def process_url_task(self, url: str, force_refresh: bool = False):
    """Celery task to process URL content with caching"""
    
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
            result = loop.run_until_complete(_process_url_async(url, db, force_refresh))
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

async def _process_url_async(url: str, db: Session, force_refresh: bool = False):
    """Async function to process URL with content change detection"""
    processor = ContentProcessor()
    vector_store = VectorStore()
    
    try:
        # Fetch content with caching
        content_data = await processor.fetch_content(url, force_refresh)
        content = content_data["content"]
        content_hash = content_data["content_hash"]
        from_cache = content_data["from_cache"]
        content_changed = content_data.get("content_changed", True)
        
        if not content or len(content.strip()) < 100:
            raise Exception("Content too short or empty")
        
        # Get URL record
        url_record = db.query(URLIngestion).filter(URLIngestion.url == url).first()
        
        # Check if we need to reprocess
        if url_record and url_record.content_hash == content_hash and not force_refresh:
            # Content hasn't changed, mark as completed
            url_record.status = "completed"
            db.commit()
            return {
                "status": "completed",
                "message": "Content unchanged, skipped processing",
                "content_hash": content_hash,
                "from_cache": from_cache
            }
        
        # Content has changed or is new, process it
        documents = processor.chunk_content(content, url)
        
        if not documents:
            raise Exception("No valid chunks created")
        
        # If content changed, remove old embeddings from vector store
        if url_record and content_changed:
            # Note: In a production system, you'd want to implement
            # vector store cleanup for changed content
            pass
        
        # Store in vector database
        vector_store.add_documents(documents)
        
        # Update database record
        if url_record:
            url_record.status = "completed"
            url_record.content_hash = content_hash
            db.commit()
        
        return {
            "status": "completed",
            "chunks_created": len(documents),
            "content_hash": content_hash,
            "from_cache": from_cache,
            "content_changed": content_changed
        }
        
    except Exception as e:
        # Update status to failed
        url_record = db.query(URLIngestion).filter(URLIngestion.url == url).first()
        if url_record:
            url_record.status = "failed"
            url_record.error_message = str(e)
            db.commit()
        raise
