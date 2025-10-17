# Scalable Web-Aware RAG Engine

A production-ready Retrieval-Augmented Generation (RAG) system that asynchronously ingests web content and enables semantic search with AI-powered question answering.

## 🏗️ Architecture & Design

### System Architecture


### Design Principles

**Asynchronous Processing**: URL ingestion runs in background workers, providing immediate API responses while processing continues asynchronously.

**Intelligent Caching**: Multi-layer caching system prevents redundant processing:
- Content hash comparison for change detection
- Embedding cache for frequently accessed content
- Redis-based distributed caching

**Microservices Architecture**: Loosely coupled services enable independent scaling and deployment.

**Fault Tolerance**: Comprehensive error handling with automatic retries and graceful degradation.

## 🛠️ Technology Stack

### Core Framework
- **FastAPI + Uvicorn**: High-performance async API framework with automatic OpenAPI documentation
- **Celery + Redis**: Distributed task queue for background processing with monitoring via Flower

### Web Content Processing
- **Playwright**: Handles JavaScript-heavy and dynamically rendered pages
- **Trafilatura**: Specialized main content extraction from web pages
- **BeautifulSoup4**: Robust HTML parsing fallback
- **LangChain Text Splitters**: Semantic-aware text chunking with overlap control

### Data Storage
- **Qdrant**: Self-hosted vector database with HNSW algorithm for efficient similarity search
- **PostgreSQL**: ACID-compliant metadata store with JSON support for flexible schemas
- **Redis**: High-performance caching and message broker

### AI/ML Components
- **sentence-transformers/all-MiniLM-L6-v2**: Open-source embedding model (384 dimensions)
- **Ollama + Llama 3.2 3B**: Local LLM for answer generation
- **tiktoken**: Accurate token counting for embedding preparation

### Infrastructure
- **Docker + Docker Compose**: Containerized deployment with environment consistency
- **Streamlit**: Interactive web interface for testing and demonstration

## 📊 Database Schema

### PostgreSQL Metadata Schema

```sql
-- URL Ingestion Tracking
CREATE TABLE url_ingestions (
    id SERIAL PRIMARY KEY,
    url VARCHAR UNIQUE NOT NULL,
    status VARCHAR DEFAULT 'pending',  -- pending, processing, completed, failed
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    error_message TEXT,
    content_hash VARCHAR  -- SHA-256 hash for change detection
);

CREATE INDEX idx_url_ingestions_url ON url_ingestions(url);
CREATE INDEX idx_url_ingestions_status ON url_ingestions(status);
```

### Qdrant Vector Store Schema

```python
# Collection Configuration
{
    "name": "web_content",
    "vectors": {
        "size": 384,  # all-MiniLM-L6-v2 embedding dimensions
        "distance": "Cosine"
    }
}

# Document Payload Structure
{
    "content": "text chunk content",
    "url": "source URL",
    "chunk_index": 0,
    "metadata": {
        "title": "page title",
        "timestamp": "2024-10-17T22:04:53Z"
    }
}
```

## 🚀 API Documentation

### Ingestion Endpoints

#### POST `/api/ingest-url`
Submit URL for asynchronous processing.

**Request Body:**
```json
{
    "url": "https://example.com/article"
}
```

**Response:**
```json
{
    "message": "URL queued for processing",
    "url": "https://example.com/article",
    "status": "pending"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/ingest-url" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com/article"}'
```

#### POST `/api/refresh-url`
Force refresh URL content even if unchanged.

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/refresh-url" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com/article"}'
```

#### GET `/api/status`
Get overall ingestion statistics.

**Response:**
```json
{
    "pending_urls": 2,
    "processing_urls": 1,
    "completed_urls": 15,
    "failed_urls": 0,
    "total_urls": 18
}
```

**cURL Example:**
```bash
curl "http://localhost:8000/api/status"
```

### Query Endpoints

#### POST `/api/query`
Query the knowledge base with semantic search.

**Request Body:**
```json
{
    "query": "What are the benefits of renewable energy?",
    "limit": 5
}
```

**Response:**
```json
{
    "answer": "Based on the ingested content, renewable energy offers several key benefits...",
    "sources": [
        {
            "url": "https://example.com/renewable-energy",
            "content_preview": "Renewable energy sources like solar and wind...",
            "relevance_score": 0.89
        }
    ],
    "query": "What are the benefits of renewable energy?"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the benefits of renewable energy?", "limit": 5}'
```

#### GET `/api/health`
Health check for all services.

**Response:**
```json
{
    "status": "healthy",
    "llm_available": true,
    "services": {
        "vector_store": "available",
        "llm": "available"
    }
}
```

## ⚙️ Setup Instructions

### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- Git

### Environment Configuration

1. **Copy environment template:**
```bash
cp .env.example .env.dev
```

2. **Configure `.env.dev`:**
```bash
# Database Configuration
POSTGRES_DB=rag_db
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Qdrant Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=web_content

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Environment
ENVIRONMENT=development

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379

# Cache Configuration
EMBEDDING_CACHE_TTL=86400
EMBEDDING_CACHE_PREFIX=emb:
CONTENT_CACHE_TTL=7200
CONTENT_CACHE_PREFIX=content:

# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2:3b

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Development Setup

1. **Clone repository:**
```bash
git clone <repository-url>
cd ask-ques-4-web
```

2. **Install Ollama and model:**
```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama service
ollama serve

# Pull Llama 3.2 model
ollama pull llama3.2:3b
```

3. **Start development environment:**
```bash
chmod +x start_dev.sh
./start_dev.sh
```

This script will:
- Start infrastructure services (Redis, PostgreSQL, Qdrant)
- Install Python dependencies
- Initialize database tables
- Start API server, Celery worker, and frontend

4. **Access services:**
- Frontend: http://localhost:8501
- API Documentation: http://localhost:8000/docs
- Qdrant Dashboard: http://localhost:6333/dashboard

### Production Deployment

1. **Configure production environment:**
```bash
cp .env.example .env.prod
# Edit .env.prod with production values
```

2. **Deploy with Docker Compose:**
```bash
chmod +x start_prod.sh
./start_prod.sh
```

3. **Access production services:**
- Frontend: http://localhost:8502
- API: http://localhost:8001
- Qdrant: http://localhost:6334

### Docker Setup

**Build and run all services:**
```bash
# Development
docker-compose -f docker/docker-compose.dev.yml up --build

# Production
docker-compose -f docker/docker-compose.prod.yml up --build -d
```

**Individual service builds:**
```bash
# API service
docker build -f docker/Dockerfile.api -t rag-api .

# Worker service
docker build -f docker/Dockerfile.worker -t rag-worker .

# Frontend service
docker build -f docker/Dockerfile.frontend -t rag-frontend .
```

### Requirements

**Core Dependencies (`requirements.txt`):**
```
fastapi==0.104.1
uvicorn==0.24.0
celery==5.3.4
redis==5.0.1
playwright==1.40.0
trafilatura==1.6.4
qdrant-client==1.7.0
psycopg2-binary==2.9.9
sentence-transformers==2.7.0
httpx==0.25.2
python-multipart==0.0.6
jinja2==3.1.2
aiofiles==23.2.1
numpy==1.24.4
torch==2.1.1
transformers==4.36.2
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.4
validators==0.22.0
pydantic-settings==2.0.3
streamlit==1.28.1
sqlalchemy==2.0.23
hiredis==2.2.3
```

## 🎯 Design Justifications

### Technology Choices

**FastAPI over Flask/Django**: Native async support crucial for I/O-bound operations like web scraping and LLM calls. Automatic OpenAPI documentation reduces development overhead.

**Celery + Redis**: Battle-tested combination for distributed task processing. Redis serves dual purpose as message broker and cache, reducing infrastructure complexity.

**Qdrant over Pinecone/Weaviate**: Self-hosted solution provides cost control and data sovereignty. HNSW algorithm offers excellent performance for similarity search.

**PostgreSQL over MongoDB**: ACID compliance ensures data consistency for ingestion tracking. JSON support provides schema flexibility when needed.

**Playwright over Requests**: Modern web requires JavaScript execution. Playwright handles SPAs and dynamic content that traditional scrapers miss.

**sentence-transformers over OpenAI**: Local embedding generation eliminates API costs and latency. Model size (384d) balances performance with resource usage.

**Ollama + Llama 3.2**: Local LLM deployment ensures privacy and cost predictability. 3B parameter model provides good quality while remaining resource-efficient.

### Architectural Decisions

**Microservices over Monolith**: Independent scaling of API, workers, and storage components. Fault isolation prevents cascade failures.

**Content Hash Comparison**: Prevents unnecessary reprocessing of unchanged content, significantly reducing computational overhead.

**Multi-layer Caching**: Embedding cache (24h TTL) and content cache (2h TTL) optimize for different access patterns and update frequencies.

**Async Processing Pipeline**: Immediate API responses improve user experience while background processing handles time-intensive operations.

## 🎬 Demo Video

**[Demo Video Link ]**: https://your-demo-video-link.com

---

## 🚀 Future Enhancements

- Kubernetes deployment manifests
- Prometheus + Grafana monitoring stack
- Advanced content filtering and quality scoring
- Multi-language embedding support
- Real-time WebSocket updates for ingestion status
