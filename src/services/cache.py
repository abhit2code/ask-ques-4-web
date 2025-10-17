import redis
import json
import hashlib
from typing import List, Optional, Any
from src.config.settings import settings

class CacheService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        self.embedding_prefix = settings.embedding_cache_prefix
        self.ttl = settings.embedding_cache_ttl
    
    def _get_text_hash(self, text: str) -> str:
        """Generate hash for text to use as cache key"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding for text"""
        try:
            key = f"{self.embedding_prefix}{self._get_text_hash(text)}"
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception:
            return None
    
    def set_embedding(self, text: str, embedding: List[float]) -> bool:
        """Cache embedding for text"""
        try:
            key = f"{self.embedding_prefix}{self._get_text_hash(text)}"
            self.redis_client.setex(key, self.ttl, json.dumps(embedding))
            return True
        except Exception:
            return False
    
    def get_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Get cached embeddings for multiple texts"""
        try:
            keys = [f"{self.embedding_prefix}{self._get_text_hash(text)}" for text in texts]
            cached_values = self.redis_client.mget(keys)
            return [json.loads(val) if val else None for val in cached_values]
        except Exception:
            return [None] * len(texts)
    
    def set_embeddings_batch(self, texts: List[str], embeddings: List[List[float]]) -> bool:
        """Cache embeddings for multiple texts"""
        try:
            pipe = self.redis_client.pipeline()
            for text, embedding in zip(texts, embeddings):
                key = f"{self.embedding_prefix}{self._get_text_hash(text)}"
                pipe.setex(key, self.ttl, json.dumps(embedding))
            pipe.execute()
            return True
        except Exception:
            return False
