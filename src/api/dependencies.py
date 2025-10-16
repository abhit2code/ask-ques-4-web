from src.database.connection import get_db
from src.services.vector_store import VectorStore
from src.services.llm_service import LLMService

# Dependency injection
def get_vector_store():
    return VectorStore()

def get_llm_service():
    return LLMService()

# Export database dependency
__all__ = ["get_db", "get_vector_store", "get_llm_service"]
