from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from src.api.dependencies import get_vector_store, get_llm_service
from src.services.vector_store import VectorStore
from src.services.llm_service import LLMService

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    query: str

@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(
    request: QueryRequest,
    vector_store: VectorStore = Depends(get_vector_store),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Query the knowledge base"""
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        # Search for relevant documents
        search_results = vector_store.search(request.query, limit=request.limit)
        
        if not search_results:
            return QueryResponse(
                answer="I don't have any information to answer this question. Please try ingesting some URLs first.",
                sources=[],
                query=request.query
            )
        
        # Generate answer using LLM
        answer = await llm_service.generate_answer(request.query, search_results)
        
        # Format sources
        sources = [
            {
                "url": result["url"],
                "content_preview": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],
                "relevance_score": result["score"]
            }
            for result in search_results
        ]
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            query=request.query
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@router.get("/health")
async def health_check(llm_service: LLMService = Depends(get_llm_service)):
    """Health check endpoint"""
    llm_available = await llm_service.check_model_availability()
    
    return {
        "status": "healthy",
        "llm_available": llm_available,
        "services": {
            "vector_store": "available",
            "llm": "available" if llm_available else "unavailable"
        }
    }
