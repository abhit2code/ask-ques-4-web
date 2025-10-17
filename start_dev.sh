#!/bin/bash

# Development Environment Management Script

set -e

# Change to script directory (project root)
cd "$(dirname "$0")"

COMPOSE_FILE="docker/docker-compose.dev.yml"
PROJECT_NAME="rag-development"

show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  up        Start infrastructure services and run backend locally"
    echo "  down      Stop all services"
    echo "  build     Build/rebuild Docker images"
    echo "  services  Start only infrastructure services"
    echo "  backend   Run backend locally (requires services to be running)"
    echo "  frontend  Run frontend locally"
    echo "  logs      Show logs from infrastructure services"
    echo "  status    Show status of infrastructure services"
    echo "  help      Show this help message"
    echo ""
}

check_requirements() {
    if ! command -v docker &> /dev/null; then
        echo " Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo " Docker Compose is not installed"
        exit 1
    fi
    
    if [ ! -f ".env.dev" ]; then
        echo " .env.dev file not found"
        exit 1
    fi
    
    if [ ! -d "venv" ]; then
        echo " Virtual environment not found. Please create one with: python -m venv venv"
        exit 1
    fi
}

load_env() {
    if [ -f ".env.dev" ]; then
        export $(cat .env.dev | grep -v '^#' | xargs)
    fi
}

# Service-specific build markers
WORKER_BUILD_MARKER=".last_build_worker_dev"

needs_worker_rebuild() {
    [ ! -f "$WORKER_BUILD_MARKER" ] && return 0
    find src/workers src/services src/config requirements.txt docker/Dockerfile.worker -newer "$WORKER_BUILD_MARKER" 2>/dev/null | head -1 | grep -q .
}

build_service() {
    local service=$1
    local marker=$2
    echo "🔨 Building $service image..."
    docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE build $service
    touch "$marker"
    echo " $service image built"
}

smart_build() {
    local built_any=false
    
    if needs_worker_rebuild; then
        echo " Worker changes detected"
        build_service "worker" "$WORKER_BUILD_MARKER"
        built_any=true
    fi
    
    if [ "$built_any" = false ]; then
        echo " All images are up to date, skipping build"
    fi
}

build_images() {
    echo " Building Docker images..."
    docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE build --no-cache
    echo " Docker images built successfully"
}

start_services() {
    echo "Starting development infrastructure services..."
    
    # Start services
    docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE up -d
    echo " Infrastructure services started"
    
    # Wait for services to be ready
    echo " Waiting for services to be ready..."
    sleep 5
    
    # Initialize database
    echo " Initializing database..."
    source venv/bin/activate
    python scripts/init_db.py || echo "⚠️  Database might already be initialized"
    
    echo " Development environment ready"
    echo ""
    echo "Infrastructure services:"
    echo "  - Redis: localhost:6379"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Qdrant: localhost:6333"
}

stop_services() {
    echo " Stopping development services..."
    docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE down
    echo " Development services stopped"
}

run_backend() {
    echo " Starting backend API server..."
    load_env
    source venv/bin/activate
    export PYTHONPATH="$PWD:$PYTHONPATH"
    uvicorn src.api.main:app --host 0.0.0.0 --port 8080 --reload
}

run_frontend() {
    echo "Starting frontend server..."
    source venv/bin/activate
    streamlit run frontend.py --server.port=8501 --server.address=0.0.0.0
}

show_logs() {
    docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE logs -f
}

show_status() {
    docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE ps
}

case "${1:-help}" in
    up)
        check_requirements
        smart_build
        start_services
        echo ""
        echo "🚀 Now starting backend server..."
        run_backend
        ;;
    down)
        check_requirements
        stop_services
        ;;
    build)
        check_requirements
        build_images
        ;;
    services)
        check_requirements
        smart_build
        start_services
        ;;
    backend)
        check_requirements
        run_backend
        ;;
    frontend)
        check_requirements
        run_frontend
        ;;
    logs)
        check_requirements
        show_logs
        ;;
    status)
        check_requirements
        show_status
        ;;
    help|*)
        show_help
        ;;
esac
