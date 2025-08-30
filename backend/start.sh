#!/bin/bash

# Task Pulse Production Startup Script
# This script handles the production startup of the Task Pulse API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    error "Please do not run this script as root"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    log "Loading environment variables from .env file"
    export $(cat .env | grep -v '^#' | xargs)
else
    warn "No .env file found, using system environment variables"
fi

# Set default environment
export ENVIRONMENT=${ENVIRONMENT:-production}

log "Starting Task Pulse API in $ENVIRONMENT mode"

# Check required environment variables
required_vars=("POSTGRES_USER" "POSTGRES_PASSWORD" "POSTGRES_DB" "SUPER_SECRET")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        error "Required environment variable $var is not set"
        exit 1
    fi
done

# Create logs directory
mkdir -p logs

# Check database connection (async)
log "Checking database connection..."
python -c "
import asyncio
import sys
from db.session import check_db_connection

async def check_db():
    try:
        if await check_db_connection():
            print('Database connection successful')
            return True
        else:
            print('Database connection failed')
            return False
    except Exception as e:
        print(f'Database connection error: {e}')
        return False

if __name__ == '__main__':
    result = asyncio.run(check_db())
    if not result:
        sys.exit(1)
"

if [ $? -ne 0 ]; then
    error "Database connection check failed"
    exit 1
fi

# Run database migrations
log "Running database migrations..."
alembic upgrade head

if [ $? -ne 0 ]; then
    error "Database migration failed"
    exit 1
fi

# Start the application
if [ "$ENVIRONMENT" = "production" ]; then
    log "Starting production server with Gunicorn..."
    exec gunicorn main:app \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --timeout 120 \
        --keep-alive 2 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --access-logfile logs/access.log \
        --error-logfile logs/error.log \
        --log-level info
else
    log "Starting development server with Uvicorn..."
    exec uvicorn main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --log-level info
fi 