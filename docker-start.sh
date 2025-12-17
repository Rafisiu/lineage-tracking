#!/bin/bash

# Docker deployment startup script

set -e

echo "ClickHouse Migration & Query App - Docker Deployment"
echo "======================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down 2>/dev/null || true
echo ""

# Build images
echo "Building Docker images..."
docker-compose build
echo ""

# Start services
echo "Starting services..."
docker-compose up -d
echo ""

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check service status
echo "Service Status:"
docker-compose ps
echo ""

# Get container IPs
FRONTEND_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' clickhouse-migration-frontend 2>/dev/null || echo "N/A")
BACKEND_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' clickhouse-migration-backend 2>/dev/null || echo "N/A")

echo "Network Information:"
echo "   Frontend: $FRONTEND_IP"
echo "   Backend:  $BACKEND_IP"
echo ""

# Test health endpoints
echo "Health Checks:"

# Test backend
BACKEND_HEALTH=$(docker-compose exec -T backend wget -q -O - http://localhost:3000/health 2>/dev/null || echo "")
if [ ! -z "$BACKEND_HEALTH" ]; then
    echo "   Backend API: Healthy"
else
    echo "   Backend API: Not responding"
fi

echo ""
echo "======================================================="
echo "Deployment Complete!"
echo "======================================================="
echo ""
echo "Access URL:"
echo "   HTTP: http://localhost"
echo ""
echo "Useful Commands:"
echo "   View logs:        docker-compose logs -f"
echo "   Stop services:    docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Check status:     docker-compose ps"
echo ""
echo "Documentation:"
echo "   Full guide: DOCKER_DEPLOYMENT.md"
echo ""
