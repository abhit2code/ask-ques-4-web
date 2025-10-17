#!/bin/bash

# Production Environment Management Script

set -e

# Change to script directory (project root)
cd "$(dirname "$0")"

COMPOSE_FILE="docker/docker-compose.prod.yml"
PROJECT_NAME="rag-production"
BUILD_MARKER=".last_build"

show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  up      Start all production services (builds if needed)"
    echo "  down    Stop all production services"
    echo "  build   Build/rebuild all Docker images"
    echo "  deploy  Build and deploy (force rebuild + start)"
    echo "  restart Restart all production services"
    echo "  logs    Show logs from all services"
    echo "  status  Show status of all services"
    echo "  help    Show this help message"
    echo ""
}

check_requirements() {
    if ! command -v docker &> /dev/null; then
        echo "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "Docker Compose is not installed"
        exit 1
    fi
    
    if [ ! -f ".env.prod" ]; then
        echo ".env.prod file not found"
        exit 1
    fi
}

# Service-specific build markers
API_BUILD_MARKER=".last_build_api"
WORKER_BUILD_MARKER=".last_build_worker"
FRONTEND_BUILD_MARKER=".last_build_frontend"

needs_api_rebuild() {
    [ ! -f "$API_BUILD_MARKER" ] && return 0
    find src/api src/services src/config requirements.txt docker/Dockerfile.api -newer "$API_BUILD_MARKER" 2>/dev/null | head -1 | grep -q .
}

needs_worker_rebuild() {
    [ ! -f "$WORKER_BUILD_MARKER" ] && return 0
    find src/workers src/services src/config requirements.txt docker/Dockerfile.worker -newer "$WORKER_BUILD_MARKER" 2>/dev/null | head -1 | grep -q .
}

needs_frontend_rebuild() {
    [ ! -f "$FRONTEND_BUILD_MARKER" ] && return 0
    find frontend.py docker/Dockerfile.frontend -newer "$FRONTEND_BUILD_MARKER" 2>/dev/null | head -1 | grep -q .
}

build_service() {
    local service=$1
    local marker=$2
    echo "🔨 Building $service image..."
    docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE build $service
    touch "$marker"
    echo "$service image built"
}

smart_build() {
    local built_any=false
    
    if needs_api_rebuild; then
        echo "API changes detected"
        build_service "api" "$API_BUILD_MARKER"
        built_any=true
    fi
    
    if needs_worker_rebuild; then
        echo "Worker changes detected"
        build_service "worker" "$WORKER_BUILD_MARKER"
        built_any=true
    fi
    
    if needs_frontend_rebuild; then
        echo "Frontend changes detected"
        build_service "frontend" "$FRONTEND_BUILD_MARKER"
        built_any=true
    fi
    
    if [ "$built_any" = false ]; then
        echo "All images are up to date, skipping build"
    fi
    
    # Update global marker for compatibility
    touch "$BUILD_MARKER"
}

build_images() {
    echo "Force building all production Docker images..."
    docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE build --no-cache
    
    # Update all markers
    touch "$BUILD_MARKER"
    touch "$API_BUILD_MARKER"
    touch "$WORKER_BUILD_MARKER" 
    touch "$FRONTEND_BUILD_MARKER"
    echo "All production images built successfully"
}

start_services() {
    echo "Starting production services..."
    
    # Smart build check
    smart_build
    
    # Start services
    docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE up -d
    echo "Production services started"
    echo ""
    echo "Services available at:"
    echo "  - API: http://localhost:8001"
    echo "  - Frontend: http://localhost:8502"
    echo "  - API Docs: http://localhost:8001/docs"
}

deploy_services() {
    echo "Deploying production services..."
    
    # Force rebuild
    build_images
    
    # Stop existing services
    docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE down
    
    # Start services
    docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE up -d
    echo "Production deployment complete"
    echo ""
    echo "Services available at:"
    echo "  - API: http://localhost:8001"
    echo "  - Frontend: http://localhost:8502"
    echo "  - API Docs: http://localhost:8001/docs"
}

stop_services() {
    echo "Stopping production services..."
    docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE down
    echo "Production services stopped"
}

restart_services() {
    echo " Restarting production services..."
    docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE restart
    echo " Production services restarted"
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
        start_services
        ;;
    down)
        check_requirements
        stop_services
        ;;
    build)
        check_requirements
        build_images
        ;;
    deploy)
        check_requirements
        deploy_services
        ;;
    restart)
        check_requirements
        restart_services
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
