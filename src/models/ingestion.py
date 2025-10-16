from sqlalchemy import Column, String, DateTime, Text, Integer
from datetime import datetime
from src.database.connection import Base

class URLIngestion(Base):
    __tablename__ = "url_ingestions"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_message = Column(Text, nullable=True)
    content_hash = Column(String, nullable=True)
