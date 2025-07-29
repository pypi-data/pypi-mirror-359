#!/bin/bash

# CyborgDB Service entrypoint script
# Supports both docker run with -e flags and docker-compose

echo "Starting CyborgDB Service..."
echo "Version: ${GIT_VERSION:-unknown}"

# Function to show usage examples
show_usage() {
    echo ""
    echo "Usage Examples:"
    echo ""
    echo "1. Docker run with environment variables:"
    echo "   docker run -p 8000:8000 \\"
    echo "     -e CYBORGDB_API_KEY='your-api-key' \\"
    echo "     -e CYBORGDB_DB_TYPE='redis' \\"
    echo "     -e CYBORGDB_CONNECTION_STRING='host:localhost,port:6379,db:0' \\"
    echo "     cyborgdb-service:latest"
    echo ""
    echo "2. Docker run with .env file:"
    echo "   docker run -p 8000:8000 --env-file .env cyborgdb-service:latest"
    echo ""
    echo "3. Docker Compose (copy docker-compose.example.yml):"
    echo "   docker-compose up"
    echo ""
    echo "Required Environment Variables:"
    echo "   CYBORGDB_API_KEY        - Your CyborgDB API key"
    echo "   CYBORGDB_DB_TYPE        - Database type (e.g., 'redis')"
    echo "   CYBORGDB_CONNECTION_STRING - Database connection string"
    echo ""
    echo "Documentation: https://github.com/your-org/cyborgdb-service"
}

# Check all required environment variables
MISSING_VARS=()

if [ -z "$CYBORGDB_API_KEY" ]; then
    MISSING_VARS+=("CYBORGDB_API_KEY")
fi

if [ -z "$CYBORGDB_DB_TYPE" ]; then
    MISSING_VARS+=("CYBORGDB_DB_TYPE")
fi

if [ -z "$CYBORGDB_CONNECTION_STRING" ]; then
    MISSING_VARS+=("CYBORGDB_CONNECTION_STRING")
fi

# If any variables are missing, show error and exit
if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo ""
    echo "ERROR: Required environment variables are missing:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    show_usage
    exit 1
fi

# Show current configuration
echo "Configuration:"
echo "   API Key: ${CYBORGDB_API_KEY:0:12}***"
echo "   DB Type: $CYBORGDB_DB_TYPE"
echo "   Connection: $CYBORGDB_CONNECTION_STRING"
echo ""
echo "Starting server on port 8000..."
echo "   Health check: http://localhost:8000/v1/health"
echo "   API docs: http://localhost:8000/docs"
echo ""

# Start the application using the main() function which handles everything
exec conda run --no-capture-output -n cyborgdb-service python -m cyborgdb_service.main