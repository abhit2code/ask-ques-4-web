from sentence_transformers import SentenceTransformer
from typing import List
from src.config.settings import settings

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model)
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        return self.model.encode(text).tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return self.model.encode(texts).tolist()
