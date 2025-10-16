import httpx
from typing import List, Dict, Any
from src.config.settings import settings

class LLMService:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.llm_model
    
    async def generate_answer(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Generate answer using retrieved context"""
        
        # Prepare context
        context = "\n\n".join([
            f"Source: {chunk['url']}\nContent: {chunk['content']}"
            for chunk in context_chunks
        ])
        
        prompt = f"""Based on the following context, answer the question. If the answer cannot be found in the context, say "I don't have enough information to answer this question."

Context:
{context}

Question: {query}

Answer:"""
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "Sorry, I couldn't generate an answer.")
                else:
                    return "Sorry, the language model is not available."
                    
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    async def check_model_availability(self) -> bool:
        """Check if the LLM model is available"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    return any(model["name"].startswith(self.model) for model in models)
                return False
        except:
            return False
