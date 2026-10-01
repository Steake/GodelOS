#!/bin/bash

# GödelOS Backend Startup Script
# Simple shell script to start the GödelOS backend API server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: ./backend/start.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --debug     Start backend in debug mode with auto-reload"
    echo "  --uvicorn   Start directly via uvicorn with auto-reload"
    echo "  --install   Install backend dependencies before starting"
    echo "  --help, -h  Show this help message"
    exit 0
fi

echo -e "${BLUE}Starting GödelOS Backend API Server${NC}"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo -e "${RED}Error: Please run this script from the GödelOS root directory${NC}"
    exit 1
fi

PROJECT_ROOT="$(pwd)"

# Auto-detect and activate virtual environment if not already active
PYTHON_BIN="python3"
if [ -n "$VIRTUAL_ENV" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
    PYTHON_BIN="$VIRTUAL_ENV/bin/python"
elif [ -d "$PROJECT_ROOT/godelos_venv" ] && [ -x "$PROJECT_ROOT/godelos_venv/bin/python" ]; then
    echo -e "${GREEN}Found virtual environment in godelos_venv, activating...${NC}"
    # shellcheck disable=SC1091
    source "$PROJECT_ROOT/godelos_venv/bin/activate"
    PYTHON_BIN="$PROJECT_ROOT/godelos_venv/bin/python"
elif [ -d "$PROJECT_ROOT/venv" ] && [ -x "$PROJECT_ROOT/venv/bin/python" ]; then
    echo -e "${GREEN}Found virtual environment in venv, activating...${NC}"
    # shellcheck disable=SC1091
    source "$PROJECT_ROOT/venv/bin/activate"
    PYTHON_BIN="$PROJECT_ROOT/venv/bin/python"
fi

# Set up environment
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"
export GODELOS_ENVIRONMENT="${GODELOS_ENVIRONMENT:-development}"

echo -e "${YELLOW}Environment: ${GODELOS_ENVIRONMENT}${NC}"
echo -e "${YELLOW}Python Path: ${PYTHONPATH}${NC}"

# Check Python version
python_version=$("$PYTHON_BIN" --version 2>&1 | awk '{print $2}')
echo -e "${YELLOW}Python Binary: ${PYTHON_BIN}${NC}"
echo -e "${YELLOW}Python Version: ${python_version}${NC}"

# Verify uvicorn presence
if ! "$PYTHON_BIN" -c "import uvicorn" 2>/dev/null; then
    echo -e "${RED}Error: 'uvicorn' is not installed in the active Python environment ($PYTHON_BIN).${NC}"
    echo -e "${YELLOW}Please initialize your environment with:${NC}"
    echo -e "  ./setup_venv.sh"
    echo -e "  source godelos_venv/bin/activate"
    exit 1
fi

# Install dependencies if needed
if [ "$1" = "--install" ]; then
    echo -e "${BLUE}Installing dependencies...${NC}"
    "$PYTHON_BIN" -m pip install -r backend/requirements.txt
    echo -e "${GREEN}Dependencies installed${NC}"
fi

# Create logs directory
mkdir -p logs backend/logs

# Check if port is available
PORT=${GODELOS_PORT:-8000}
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}Error: Port $PORT is already in use${NC}"
    echo "Please stop the existing service or use a different port:"
    echo "  export GODELOS_PORT=3001"
    exit 1
fi

# Start the server
echo -e "${GREEN}Starting server on port $PORT...${NC}"
echo -e "${BLUE}API Documentation will be available at: http://localhost:$PORT/docs${NC}"
echo -e "${BLUE}WebSocket endpoint: ws://localhost:$PORT/ws/unified-cognitive-stream${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Determine startup method
if [ "$1" = "--debug" ] || [ "$GODELOS_DEBUG" = "true" ]; then
    echo -e "${YELLOW}Starting in debug mode with auto-reload...${NC}"
    "$PYTHON_BIN" backend/start_server.py --debug --log-level DEBUG
elif [ "$1" = "--uvicorn" ]; then
    echo -e "${YELLOW}Starting with uvicorn directly...${NC}"
    "$PYTHON_BIN" -m uvicorn backend.unified_server:app --host 0.0.0.0 --port "$PORT" --reload
else
    echo -e "${GREEN}Starting in production mode...${NC}"
    "$PYTHON_BIN" backend/start_server.py --host 0.0.0.0 --port "$PORT"
fi
