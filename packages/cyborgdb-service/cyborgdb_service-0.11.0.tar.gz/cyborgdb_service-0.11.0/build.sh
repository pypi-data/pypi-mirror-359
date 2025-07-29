#!/bin/bash

# Build script for CyborgDB Service Docker image

set -e  # Exit on any error

# Configuration
IMAGE_NAME="cyborgdb-service"
IMAGE_TAG="${1:-latest}"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

echo "Building Docker image: ${FULL_IMAGE_NAME}"

# Check if required files exist
if [ ! -f "environment.yml" ]; then
    echo "Error: environment.yml not found!"
    exit 1
fi

if [ ! -f "cyborgdb_service/main.py" ]; then
    echo "Error: cyborgdb_service/main.py not found!"
    exit 1
fi

# Check for cyborgdb installation option
if [ ! -f ".cyborglicense" ] && [ -z "$CYBORGDB_TOKEN" ]; then
    echo "Warning: Neither .cyborglicense file nor CYBORGDB_TOKEN environment variable found."
    echo "Make sure to either:"
    echo "1. Place .cyborglicense file in the root directory (for local build option)"
    echo "2. Set CYBORGDB_TOKEN environment variable and uncomment pip install line in Dockerfile"
fi

# Build the Docker image
echo "Starting Docker build..."
if groups $USER | grep &>/dev/null '\bdocker\b'; then
    docker build -t "${FULL_IMAGE_NAME}" .
else
    echo "User not in docker group, using sudo..."
    sudo docker build -t "${FULL_IMAGE_NAME}" .
fi

if [ $? -eq 0 ]; then
    echo "Docker image built successfully: ${FULL_IMAGE_NAME}"
    echo ""
    echo "To run the container:"
    echo "  docker run -p 8000:8000 ${FULL_IMAGE_NAME}"
    echo ""
    echo "Or use docker-compose:"
    echo "  docker-compose up"
    echo ""
    echo "Image size:"
    if groups $USER | grep &>/dev/null '\bdocker\b'; then
        docker images "${FULL_IMAGE_NAME}" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
    else
        sudo docker images "${FULL_IMAGE_NAME}" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
    fi
else
    echo "Docker build failed!"
    exit 1
fi