import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Cache Configuration
    embedding_cache_ttl: int = Field(default=86400, env="EMBEDDING_CACHE_TTL")  # 24 hours
    embedding_cache_prefix: str = Field(default="emb:", env="EMBEDDING_CACHE_PREFIX")
    content_cache_ttl: int = Field(default=7200, env="CONTENT_CACHE_TTL")  # 2 hours
    content_cache_prefix: str = Field(default="content:", env="CONTENT_CACHE_PREFIX")
    
    # PostgreSQL Configuration - Single database
    postgres_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/rag_engine", 
        env="POSTGRES_URL"
    )
    
    # Qdrant Configuration - Single collection
    qdrant_url: str = Field(default="http://localhost:6333", env="QDRANT_URL")
    qdrant_collection_name: str = Field(default="web_content", env="QDRANT_COLLECTION_NAME")
    
    # API Configuration
    api_port: int = Field(default=8000, env="API_PORT")
    
    # Embedding Model
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", 
        env="EMBEDDING_MODEL"
    )
    
    # LLM Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    llm_model: str = Field(default="llama3.2:3b", env="LLM_MODEL")
    
    # Text Processing
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    
    class Config:
        case_sensitive = False

# Global settings instance
settings = Settings()
