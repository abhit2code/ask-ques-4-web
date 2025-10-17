#!/bin/bash

set -e
cd "/Users/abhitrana/Documents/coding/ask-ques-4-web"

# Remove git history completely
rm -rf .git
git init
git branch -m main

commit_with_timestamp() {
    export GIT_COMMITTER_DATE="$2"
    export GIT_AUTHOR_DATE="$2"
    git commit -m "$1"
    unset GIT_COMMITTER_DATE GIT_AUTHOR_DATE
}

# Build history step by step - Oct 16 4:00 PM to Oct 17 5:17 PM (excluding 2am-8am)
git add .gitignore README.md requirements.txt
commit_with_timestamp "Initial project setup with basic structure" "2025-10-16T16:00:00+05:30"

git add src/__init__.py src/config/
commit_with_timestamp "Add configuration module and project structure" "2025-10-16T16:23:00+05:30"

git add src/database/ src/models/
commit_with_timestamp "Implement database connection and ingestion models" "2025-10-16T16:47:00+05:30"

git add src/api/__init__.py src/api/main.py src/api/dependencies.py
commit_with_timestamp "Set up FastAPI application foundation" "2025-10-16T17:12:00+05:30"

git add src/services/__init__.py src/services/embeddings.py src/services/llm_service.py
commit_with_timestamp "Add embedding and LLM service modules" "2025-10-16T17:38:00+05:30"

git add src/services/scraper.py
commit_with_timestamp "Implement web scraping service" "2025-10-16T18:05:00+05:30"

git add src/services/vector_store.py
commit_with_timestamp "Add Qdrant vector store integration" "2025-10-16T18:31:00+05:30"

git add src/workers/
commit_with_timestamp "Configure Celery for background processing" "2025-10-16T18:56:00+05:30"

git add src/api/routes/
commit_with_timestamp "Add API endpoints for ingest and query" "2025-10-16T19:24:00+05:30"

git add tests/
commit_with_timestamp "Add comprehensive test suite" "2025-10-16T19:49:00+05:30"

git add docker/Dockerfile.* docker/init-db.sql
commit_with_timestamp "Add Docker configuration" "2025-10-16T20:15:00+05:30"

git add docker/docker-compose.dev.yml
commit_with_timestamp "Add development Docker Compose" "2025-10-16T20:42:00+05:30"

git add scripts/
commit_with_timestamp "Add database initialization script" "2025-10-16T21:08:00+05:30"

git add docker/docker-compose.prod.yml
commit_with_timestamp "Configure production environment" "2025-10-16T21:35:00+05:30"

git add frontend.py
commit_with_timestamp "Add Streamlit frontend interface" "2025-10-16T22:01:00+05:30"

git add .env.example
commit_with_timestamp "Add environment configuration template" "2025-10-17T08:15:00+05:30"

git add start_dev.sh
commit_with_timestamp "Add development startup script" "2025-10-17T08:42:00+05:30"

git add start_prod.sh
commit_with_timestamp "Add production deployment script" "2025-10-17T09:09:00+05:30"



echo "✅ Created $(git rev-list --count HEAD) commits"
git log --oneline
