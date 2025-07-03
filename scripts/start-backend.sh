#!/bin/bash

# GödelOS Backend Startup Script
# Starts the GödelOS cognitive transparency backend API server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Script info
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/../backend/"

echo -e "${PURPLE}🧠 GödelOS Backend Startup${NC}"
echo -e "${BLUE}=============================${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "$BACKEND_DIR/main.py" ]; then
    echo -e "${RED}❌ Error: Backend directory not found at $BACKEND_DIR${NC}"
    echo -e "${YELLOW}   Please run this script from the GödelOS root directory${NC}"
    exit 1
fi

# Check if backend startup script exists
if [ ! -f "$BACKEND_DIR/../backend/start-backend.sh" ]; then
    echo -e "${RED}❌ Error: Backend start.sh not found${NC}"
    exit 1
fi

# Set environment variables
export PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH}"
export GODELOS_ENVIRONMENT="${GODELOS_ENVIRONMENT:-development}"
export GODELOS_PORT="${GODELOS_PORT:-8000}"

echo -e "${BLUE}📍 Working Directory: ${SCRIPT_DIR}${NC}"
echo -e "${BLUE}🐍 Python Path: ${PYTHONPATH}${NC}"
echo -e "${BLUE}🌍 Environment: ${GODELOS_ENVIRONMENT}${NC}"
echo -e "${BLUE}🔌 Port: ${GODELOS_PORT}${NC}"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 not found${NC}"
    echo -e "${YELLOW}   Please install Python 3.8 or higher${NC}"
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python Version: ${python_version}${NC}"

# Check virtual environment recommendation
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Warning: No virtual environment detected${NC}"
    echo -e "${YELLOW}   Consider activating: source backend/venv/bin/activate${NC}"
    echo ""
fi

# Check if dependencies are installed
if [ ! -d "$BACKEND_DIR/venv" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}📦 Setting up virtual environment...${NC}"
    if [ "$1" = "--setup" ] || [ "$1" = "--install" ]; then
        cd "$BACKEND_DIR"
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Virtual environment created and dependencies installed${NC}"
        cd "$SCRIPT_DIR"
    else
        echo -e "${YELLOW}   Run with --setup to create virtual environment and install dependencies${NC}"
        echo ""
    fi
fi

# Create necessary directories
mkdir -p "$BACKEND_DIR/logs"
mkdir -p "$BACKEND_DIR/storage"
mkdir -p "$BACKEND_DIR/knowledge_storage"

echo -e "${GREEN}✅ Backend directories verified${NC}"

# Parse arguments
MODE="production"
DEBUG_FLAG=""
INSTALL_FLAG=""

for arg in "$@"; do
    case $arg in
        --debug)
            MODE="debug"
            DEBUG_FLAG="--debug"
            ;;
        --dev|--development)
            MODE="development"
            ;;
        --install|--setup)
            INSTALL_FLAG="--install"
            ;;
        --uvicorn)
            MODE="uvicorn"
            ;;
        --help|-h)
            echo -e "${BLUE}GödelOS Backend Startup Options:${NC}"
            echo ""
            echo -e "${YELLOW}Modes:${NC}"
            echo "  --debug        Start in debug mode with auto-reload"
            echo "  --dev          Start in development mode"
            echo "  --uvicorn      Start with uvicorn directly"
            echo "  (default)      Production mode"
            echo ""
            echo -e "${YELLOW}Options:${NC}"
            echo "  --install      Install dependencies first"
            echo "  --setup        Setup virtual environment and install dependencies"
            echo "  --help         Show this help message"
            echo ""
            echo -e "${YELLOW}Environment Variables:${NC}"
            echo "  GODELOS_PORT=8000        Port to run on"
            echo "  GODELOS_DEBUG=true       Enable debug mode"
            echo "  GODELOS_ENVIRONMENT=dev  Set environment"
            echo ""
            exit 0
            ;;
    esac
done

# Display startup mode
case $MODE in
    debug)
        echo -e "${YELLOW}🔧 Starting in DEBUG mode with auto-reload${NC}"
        ;;
    development)
        echo -e "${BLUE}🛠️  Starting in DEVELOPMENT mode${NC}"
        ;;
    uvicorn)
        echo -e "${PURPLE}🚀 Starting with uvicorn directly${NC}"
        ;;
    *)
        echo -e "${GREEN}🏭 Starting in PRODUCTION mode${NC}"
        ;;
esac

echo ""
echo -e "${BLUE}🌐 API Documentation: http://localhost:${GODELOS_PORT}/docs${NC}"
echo -e "${BLUE}🔌 WebSocket Endpoint: ws://localhost:${GODELOS_PORT}/ws/cognitive-stream${NC}"
echo -e "${BLUE}🧠 Cognitive State API: http://localhost:${GODELOS_PORT}/api/cognitive/state${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Change to backend directory and run the startup script
cd "$SCRIPT_DIR"  # Stay in root directory, not backend directory

# Make sure the backend start script is executable
chmod +x "$BACKEND_DIR/start-backend.sh"

# Execute the backend start script with appropriate flags from root directory
if [ -n "$INSTALL_FLAG" ]; then
    "$BACKEND_DIR/start-backend.sh" $INSTALL_FLAG $DEBUG_FLAG
else
    "$BACKEND_DIR/start-backend.sh" $DEBUG_FLAG
fi
