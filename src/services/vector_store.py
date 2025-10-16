from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import hashlib
from typing import List, Dict, Any
from src.config.settings import settings
from src.services.embeddings import EmbeddingService

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection_name = settings.qdrant_collection_name
        self.embedding_service = EmbeddingService()
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,  # all-MiniLM-L6-v2 embedding size
                        distance=Distance.COSINE
                    )
                )
        except Exception as e:
            # Collection might already exist, which is fine
            pass
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to vector store"""
        points = []
        for doc in documents:
            text = doc["content"]
            embedding = self.embedding_service.embed_text(text)
            
            # Create unique ID based on content hash
            doc_id = hashlib.md5(text.encode()).hexdigest()
            
            point = PointStruct(
                id=doc_id,
                vector=embedding,
                payload={
                    "content": text,
                    "url": doc["url"],
                    "chunk_index": doc.get("chunk_index", 0),
                    "metadata": doc.get("metadata", {})
                }
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        query_embedding = self.embedding_service.embed_text(query)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit
        )
        
        return [
            {
                "content": result.payload["content"],
                "url": result.payload["url"],
                "score": result.score,
                "metadata": result.payload.get("metadata", {})
            }
            for result in results
        ]
