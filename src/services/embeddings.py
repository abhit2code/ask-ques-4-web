from sentence_transformers import SentenceTransformer
from typing import List
from src.config.settings import settings
from src.services.cache import CacheService

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model)
        self.cache = CacheService()
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text with caching"""
        # Try cache first
        cached_embedding = self.cache.get_embedding(text)
        if cached_embedding:
            return cached_embedding
        
        # Generate embedding
        embedding = self.model.encode(text).tolist()
        
        # Cache the result
        self.cache.set_embedding(text, embedding)
        
        return embedding
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts with caching"""
        # Check cache for all texts
        cached_embeddings = self.cache.get_embeddings_batch(texts)
        
        # Identify texts that need embedding
        texts_to_embed = []
        indices_to_embed = []
        
        for i, (text, cached) in enumerate(zip(texts, cached_embeddings)):
            if cached is None:
                texts_to_embed.append(text)
                indices_to_embed.append(i)
        
        # Generate embeddings for uncached texts
        if texts_to_embed:
            new_embeddings = self.model.encode(texts_to_embed).tolist()
            
            # Cache new embeddings
            self.cache.set_embeddings_batch(texts_to_embed, new_embeddings)
            
            # Fill in the results
            for idx, embedding in zip(indices_to_embed, new_embeddings):
                cached_embeddings[idx] = embedding
        
        return cached_embeddings
