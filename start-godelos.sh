#!/bin/bash

# GödelOS Unified Startup System
# Complete system launcher for backend and frontend
# Version: 0.2 Beta

set -e

# Colors for output
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
PURPLE="\033[0;35m"
CYAN="\033[0;36m"
WHITE="\033[1;37m"
NC="\033[0m" # No Color

# Configuration
BACKEND_PORT=${GODELOS_BACKEND_PORT:-8000}
FRONTEND_PORT=${GODELOS_FRONTEND_PORT:-1337}
BACKEND_HOST=${GODELOS_BACKEND_HOST:-0.0.0.0}
FRONTEND_HOST=${GODELOS_FRONTEND_HOST:-0.0.0.0}
FRONTEND_TYPE=${GODELOS_FRONTEND_TYPE:-auto}

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "$SCRIPT_DIR/../backend" ] && [ -d "$SCRIPT_DIR/../svelte-frontend" ]; then
    ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
else
    ROOT_DIR="$SCRIPT_DIR"
fi
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/svelte-frontend"
LOGS_DIR="$ROOT_DIR/logs"

# Auto-detect frontend type
DETECTED_FRONTEND_TYPE=""

# PID storage
BACKEND_PID=""
FRONTEND_PID=""

# Helpers for virtual environment and Python binary
get_python_bin() {
    if [ -n "$VIRTUAL_ENV" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
        echo "$VIRTUAL_ENV/bin/python"
    elif [ -d "$ROOT_DIR/godelos_venv" ] && [ -x "$ROOT_DIR/godelos_venv/bin/python" ]; then
        echo "$ROOT_DIR/godelos_venv/bin/python"
    elif [ -d "$BACKEND_DIR/venv" ] && [ -x "$BACKEND_DIR/venv/bin/python" ]; then
        echo "$BACKEND_DIR/venv/bin/python"
    else
        echo "python3"
    fi
}

activate_venv() {
    if [ -d "$ROOT_DIR/godelos_venv" ] && [ -f "$ROOT_DIR/godelos_venv/bin/activate" ]; then
        # shellcheck disable=SC1091
        source "$ROOT_DIR/godelos_venv/bin/activate"
    elif [ -d "$BACKEND_DIR/venv" ] && [ -f "$BACKEND_DIR/venv/bin/activate" ]; then
        # shellcheck disable=SC1091
        source "$BACKEND_DIR/venv/bin/activate"
    fi
}

# Create banner
show_banner() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${WHITE}                     🧠 GödelOS v0.2 Beta                      ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${CYAN}              Cognitive Architecture System                    ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${YELLOW}                  Unified Startup System                     ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Show help
show_help() {
    echo -e "${BLUE}Usage: $0 [OPTIONS]${NC}"
    echo ""
    echo -e "${YELLOW}Quick Start:${NC}"
    echo "  $0                     Start both backend and frontend"
    echo "  $0 --setup             Install dependencies and start"
    echo "  $0 --dev               Start in development mode"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  --backend-only         Start only the backend server"
    echo "  --frontend-only        Start only the frontend server"
    echo "  --svelte-frontend      Force use Svelte frontend (svelte-frontend)"
    echo "  --dev                  Development mode (auto-reload)"
    echo "  --debug                Debug mode with verbose logging"
    echo "  --setup                Install dependencies first"
    echo "  --check                Check system requirements only"
    echo "  --stop                 Stop any running GödelOS processes"
    echo "  --status               Show status of running processes"
    echo "  --logs                 Show recent logs"
    echo "  --help, -h             Show this help message"
    echo ""
    echo -e "${YELLOW}Environment Variables:${NC}"
    echo "  GODELOS_BACKEND_PORT=8000    Backend port"
    echo "  GODELOS_FRONTEND_PORT=1337   Frontend port"
    echo "  GODELOS_BACKEND_HOST=0.0.0.0 Backend host"
    echo "  GODELOS_FRONTEND_HOST=0.0.0.0 Frontend host"
    echo "  GODELOS_FRONTEND_TYPE=auto   Frontend type (auto, svelte)"
    echo ""
}

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${PURPLE}🔄 $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect and set frontend type
detect_frontend() {
    local candidate_dir="$ROOT_DIR/svelte-frontend"
    if [ -d "$candidate_dir" ] && [ -f "$candidate_dir/package.json" ]; then
        FRONTEND_DIR="$candidate_dir"
        DETECTED_FRONTEND_TYPE="svelte"
    else
        log_error "Svelte frontend not found at $candidate_dir"
        exit 1
    fi
}

# Check if port is in use
port_in_use() {
    local port=$1
    if command_exists lsof; then
        lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1
    elif command_exists netstat; then
        netstat -ln 2>/dev/null | grep ":$port " >/dev/null
    else
        timeout 1 bash -c "</dev/tcp/localhost/$port" >/dev/null 2>&1
    fi
}

# Check server endpoint health
check_endpoint_health() {
    local url=$1
    local timeout=${2:-5}
    local python_bin=$(get_python_bin)
    
    if command_exists curl; then
        curl -f -s -m "$timeout" --connect-timeout "$timeout" "$url" >/dev/null 2>&1
    elif command_exists wget; then
        wget --quiet --timeout="$timeout" --tries=1 -O /dev/null "$url" >/dev/null 2>&1
    else
        "$python_bin" -c "
import urllib.request
import socket
import sys
try:
    socket.setdefaulttimeout($timeout)
    urllib.request.urlopen('$url')
    sys.exit(0)
except:
    sys.exit(1)
" 2>/dev/null
    fi
}

# Create necessary directories
setup_directories() {
    log_step "Setting up directories..."
    mkdir -p "$LOGS_DIR"
    mkdir -p "$BACKEND_DIR/logs"
    mkdir -p "$BACKEND_DIR/storage"
    mkdir -p "$ROOT_DIR/knowledge_storage"
    mkdir -p "$ROOT_DIR/meta_knowledge_store"
    log_success "Directories created"
}

# Check system requirements
check_requirements() {
    log_step "Checking system requirements..."
    activate_venv
    local python_bin=$(get_python_bin)
    
    if ! command_exists "$python_bin" && ! command_exists python3; then
        log_error "Python 3 is required but not found"
        log_info "Please install Python 3.10+ and run ./setup_venv.sh"
        exit 1
    fi
    
    python_version=$("$python_bin" --version 2>&1 | awk "{print \$2}")
    log_success "Python $python_version found ($python_bin)"
    
    if [ ! -d "$BACKEND_DIR" ]; then
        log_error "Backend directory not found: $BACKEND_DIR"
        exit 1
    fi
    
    detect_frontend
    
    if [ -z "$FRONTEND_DIR" ] || [ ! -d "$FRONTEND_DIR" ]; then
        log_error "Svelte frontend not found at $FRONTEND_DIR"
        exit 1
    fi
    
    if [ ! -f "$FRONTEND_DIR/package.json" ]; then
        log_error "Svelte frontend package.json not found"
        exit 1
    fi
    
    log_success "All required files found"
    log_success "Frontend type: svelte ($FRONTEND_DIR)"
    
    if port_in_use $BACKEND_PORT; then
        log_warning "Backend port $BACKEND_PORT is already in use"
        return 1
    fi
    
    if port_in_use $FRONTEND_PORT; then
        log_warning "Frontend port $FRONTEND_PORT is already in use"
        return 1
    fi
    
    log_success "Ports $BACKEND_PORT and $FRONTEND_PORT are available"
    return 0
}

# Install dependencies
install_dependencies() {
    log_step "Installing dependencies..."
    detect_frontend
    
    if [ -f "$ROOT_DIR/scripts/setup_venv.sh" ]; then
        log_step "Executing automated environment setup ($ROOT_DIR/scripts/setup_venv.sh)..."
        bash "$ROOT_DIR/scripts/setup_venv.sh"
    fi
    
    activate_venv
    local python_bin=$(get_python_bin)
    
    # Frontend dependencies
    log_step "Installing Svelte frontend dependencies..."
    if ! command_exists npm; then
        log_error "npm not found - Svelte frontend requires Node.js and npm"
        exit 1
    else
        cd "$FRONTEND_DIR"
        npm install --prefer-offline --no-audit --no-fund || npm install --no-audit --no-fund
        log_success "Svelte dependencies installed"
        cd "$ROOT_DIR"
    fi
    
    # Verify critical Python dependencies
    log_step "Verifying critical dependencies..."
    "$python_bin" -c "
import sys
import importlib.util

required_modules = {
    'fastapi': 'FastAPI web framework',
    'uvicorn': 'ASGI server', 
    'pydantic': 'Data validation',
    'networkx': 'Graph analysis',
    'psutil': 'Process monitoring',
    'dotenv': 'Environment configuration',
    'websockets': 'WebSocket support',
    'aiofiles': 'Async file operations'
}

missing = []
for module, desc in required_modules.items():
    if importlib.util.find_spec(module) is None:
        missing.append(f'{module} ({desc})')

if missing:
    print(f'❌ Missing critical dependencies: {missing}')
    sys.exit(1)

print('✅ All critical backend dependencies available')
"
}

# Pre-cache ML models
cache_models() {
    log_step "Checking ML model cache..."
    activate_venv
    local python_bin=$(get_python_bin)
    
    if [ ! -f "$ROOT_DIR/scripts/cache_models.py" ]; then
        return 0
    fi
    
    local cache_dir="$ROOT_DIR/data/vector_db/model_cache"
    if [ -d "$cache_dir" ] && [ "$(ls -A "$cache_dir" 2>/dev/null | wc -l)" -gt 2 ]; then
        log_info "ML models already cached - skipping download"
        return 0
    fi
    
    log_info "Caching ML models to improve startup performance..."
    if "$python_bin" "$ROOT_DIR/scripts/cache_models.py" 2>/dev/null; then
        log_success "ML models cached successfully"
    else
        log_info "Model pre-cache skipped - models will be loaded on demand"
    fi
}

# Stop existing processes
stop_processes() {
    log_step "Stopping existing GödelOS processes..."
    
    if [ -f "$LOGS_DIR/backend.pid" ]; then
        local pid=$(cat "$LOGS_DIR/backend.pid")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            log_success "Stopped backend process (PID: $pid)"
        fi
        rm -f "$LOGS_DIR/backend.pid"
    fi
    
    if [ -f "$LOGS_DIR/frontend.pid" ]; then
        local pid=$(cat "$LOGS_DIR/frontend.pid")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            log_success "Stopped frontend process (PID: $pid)"
        fi
        rm -f "$LOGS_DIR/frontend.pid"
    fi
    
    pkill -f "uvicorn.*unified_server:app" 2>/dev/null && log_success "Stopped uvicorn processes" || true
    pkill -f "backend/start_server.py" 2>/dev/null || true
    if command_exists lsof; then
        local b_pid=$(lsof -ti :$BACKEND_PORT 2>/dev/null || true)
        if [ -n "$b_pid" ]; then
            kill -9 $b_pid 2>/dev/null || true
        fi
        local f_pid=$(lsof -ti :$FRONTEND_PORT 2>/dev/null || true)
        if [ -n "$f_pid" ]; then
            kill -9 $f_pid 2>/dev/null || true
        fi
    fi
    sleep 1
    log_success "All existing processes stopped"
}

# Start backend
start_backend() {
    log_step "Starting backend server on port $BACKEND_PORT..."
    
    activate_venv
    local python_bin=$(get_python_bin)
    
    if ! "$python_bin" -c "import uvicorn" 2>/dev/null; then
        log_error "'uvicorn' is not installed in the active environment ($python_bin)."
        log_info "Please run ./setup_venv.sh to configure the virtual environment."
        return 1
    fi
    
    # Auto-heal transformers >= 5.0.0 bug (huggingface/transformers issue #43784)
    if "$python_bin" -c "import transformers; sys.exit(0 if int(transformers.__version__.split('.')[0]) >= 5 else 1)" 2>/dev/null; then
        log_warning "Detected transformers >= 5.0.0 (causes NameError: name 'nn' is not defined in accelerate)."
        log_step "Auto-downgrading to stable transformers < 5.0.0..."
        "$python_bin" -m pip install "transformers>=4.40.0,<5.0.0" --quiet || true
    fi

    # Check transformers capability
    if "$python_bin" -c "from transformers import pipeline" 2>/dev/null; then
        log_success "transformers.pipeline ready"
    else
        log_info "transformers.pipeline in fallback mode (core symbolic reasoning and API fully operational)"
    fi
    
    export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"
    export GODELOS_ENVIRONMENT="${GODELOS_ENVIRONMENT:-development}"
    
    local cmd=("$python_bin" "-m" "uvicorn" "backend.unified_server:app" "--host" "$BACKEND_HOST" "--port" "$BACKEND_PORT")
    
    if [ "$DEBUG_MODE" = "true" ] || [ "$DEV_MODE" = "true" ]; then
        cmd+=("--reload" "--log-level" "debug")
    fi
    
    cd "$ROOT_DIR"
    "${cmd[@]}" > "$LOGS_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    
    echo "$BACKEND_PID" > "$LOGS_DIR/backend.pid"
    
    log_step "Waiting for backend initialization..."
    local attempts=0
    local max_attempts=60
    local health_checks=0
    local required_health_checks=2
    
    while [ $attempts -lt $max_attempts ]; do
        # Detect premature process exit immediately
        if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
            echo -ne "\n"
            log_error "Backend process exited prematurely (PID: $BACKEND_PID)"
            if [ -f "$LOGS_DIR/backend.log" ]; then
                log_info "Backend log output:"
                tail -25 "$LOGS_DIR/backend.log" | sed "s/^/    /"
            fi
            return 1
        fi
        
        # Check health endpoint
        if check_endpoint_health "http://localhost:$BACKEND_PORT/api/health" 3; then
            health_checks=$((health_checks + 1))
            if [ $health_checks -ge $required_health_checks ]; then
                echo -ne "\n"
                log_success "Backend server fully initialized (PID: $BACKEND_PID)"
                log_success "✅ Core endpoints responding on port $BACKEND_PORT"
                return 0
            else
                echo -ne "${YELLOW}  Backend responding... health checks: ${health_checks}/${required_health_checks}\r${NC}"
            fi
        else
            health_checks=0
            if [ $((attempts % 5)) -eq 0 ] && [ $attempts -gt 0 ]; then
                echo -ne "${YELLOW}  Starting backend server... ${attempts}s\r${NC}"
            fi
        fi
        
        sleep 1
        attempts=$((attempts + 1))
    done
    
    echo -ne "\n"
    log_error "Backend failed to respond within ${max_attempts} seconds"
    if [ -f "$LOGS_DIR/backend.log" ]; then
        log_info "Last few log lines:"
        tail -20 "$LOGS_DIR/backend.log" | sed "s/^/    /"
    fi
    return 1
}

# Configure frontend for backend connection
configure_frontend() {
    if [ "$DETECTED_FRONTEND_TYPE" = "svelte" ]; then
        log_step "Configuring Svelte frontend for backend port $BACKEND_PORT..."
        
        cat > "$FRONTEND_DIR/.env" << EOF
VITE_BACKEND_PORT=$BACKEND_PORT
VITE_BACKEND_HOST=$BACKEND_HOST
VITE_FRONTEND_PORT=$FRONTEND_PORT
EOF

        mkdir -p "$FRONTEND_DIR/public"
        cat > "$FRONTEND_DIR/public/config.js" << EOF
// GödelOS Frontend Configuration
window.GODELOS_BACKEND_PORT = '$BACKEND_PORT';
window.GODELOS_BACKEND_HOST = '$BACKEND_HOST';
window.GODELOS_FRONTEND_PORT = '$FRONTEND_PORT';
EOF
        log_success "Frontend configured for backend at $BACKEND_HOST:$BACKEND_PORT"
    fi
}

# Start frontend
start_frontend() {
    configure_frontend
    log_step "Starting svelte frontend server on port $FRONTEND_PORT..."
    
    cd "$FRONTEND_DIR"
    
    VITE_BACKEND_PORT=$BACKEND_PORT npm run dev -- --host $FRONTEND_HOST --port $FRONTEND_PORT > "$LOGS_DIR/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    
    echo $FRONTEND_PID > "$LOGS_DIR/frontend.pid"
    cd "$ROOT_DIR"
    
    local attempts=0
    local max_attempts=15
    
    while [ $attempts -lt $max_attempts ]; do
        if port_in_use $FRONTEND_PORT; then
            log_success "svelte frontend server started (PID: $FRONTEND_PID)"
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
        if [ $((attempts % 3)) -eq 0 ]; then
            echo -ne "${YELLOW}  Waiting for svelte frontend... ${attempts}/${max_attempts}\r${NC}"
        fi
    done
    
    log_error "svelte frontend failed to start within ${max_attempts} seconds"
    log_info "Check logs: tail -f $LOGS_DIR/frontend.log"
    return 1
}

# Show status
show_status() {
    echo -e "${BLUE}📊 GödelOS System Status${NC}"
    echo -e "${BLUE}========================${NC}"
    echo ""
    
    if [ -f "$LOGS_DIR/backend.pid" ]; then
        local pid=$(cat "$LOGS_DIR/backend.pid")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${GREEN}🔧 Backend:  Running (PID: $pid, Port: $BACKEND_PORT)${NC}"
        else
            echo -e "${RED}🔧 Backend:  Stopped (stale PID file)${NC}"
        fi
    elif port_in_use $BACKEND_PORT; then
        echo -e "${YELLOW}🔧 Backend:  Running (unknown PID, Port: $BACKEND_PORT)${NC}"
    else
        echo -e "${RED}🔧 Backend:  Stopped${NC}"
    fi
    
    if [ -f "$LOGS_DIR/frontend.pid" ]; then
        local pid=$(cat "$LOGS_DIR/frontend.pid")
        if kill -0 "$pid" 2>/dev/null; then
            detect_frontend
            echo -e "${GREEN}🌐 Frontend: Running ($DETECTED_FRONTEND_TYPE, PID: $pid, Port: $FRONTEND_PORT)${NC}"
        else
            echo -e "${RED}🌐 Frontend: Stopped (stale PID file)${NC}"
        fi
    elif port_in_use $FRONTEND_PORT; then
        echo -e "${YELLOW}🌐 Frontend: Running (unknown PID, Port: $FRONTEND_PORT)${NC}"
    else
        echo -e "${RED}🌐 Frontend: Stopped${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}🔗 Access URLs:${NC}"
    echo -e "   Frontend:  ${CYAN}http://localhost:$FRONTEND_PORT${NC}"
    echo -e "   Backend:   ${CYAN}http://localhost:$BACKEND_PORT${NC}"
    echo -e "   API Docs:  ${CYAN}http://localhost:$BACKEND_PORT/docs${NC}"
    echo -e "   WebSocket: ${CYAN}ws://localhost:$BACKEND_PORT/ws/unified-cognitive-stream${NC}"
    echo ""
}

# Show recent logs
show_logs() {
    echo -e "${BLUE}📄 Recent Logs${NC}"
    echo -e "${BLUE}==============${NC}"
    echo ""
    
    if [ -f "$LOGS_DIR/backend.log" ]; then
        echo -e "${YELLOW}Backend Logs (last 10 lines):${NC}"
        tail -10 "$LOGS_DIR/backend.log"
        echo ""
    fi
    
    if [ -f "$LOGS_DIR/frontend.log" ]; then
        echo -e "${YELLOW}Frontend Logs (last 10 lines):${NC}"
        tail -10 "$LOGS_DIR/frontend.log"
        echo ""
    fi
}

# Cleanup function
cleanup() {
    echo ""
    log_step "Shutting down GödelOS system..."
    
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
        log_success "Backend server stopped"
    fi
    
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null || true
        log_success "Frontend server stopped"
    fi
    
    rm -f "$LOGS_DIR/backend.pid" "$LOGS_DIR/frontend.pid"
    echo -e "${PURPLE}👋 GödelOS system shutdown complete${NC}"
    exit 0
}

# Main execution logic
main() {
    SETUP_FLAG=false
    BACKEND_ONLY=false
    FRONTEND_ONLY=false
    DEBUG_MODE=false
    DEV_MODE=false
    CHECK_ONLY=false
    STOP_ONLY=false
    STATUS_ONLY=false
    LOGS_ONLY=false
    
    for arg in "$@"; do
        case $arg in
            --setup|--install)
                SETUP_FLAG=true
                ;;
            --backend-only)
                BACKEND_ONLY=true
                ;;
            --frontend-only)
                FRONTEND_ONLY=true
                ;;
            --svelte-frontend)
                FRONTEND_TYPE="svelte"
                ;;
            --debug)
                DEBUG_MODE=true
                ;;
            --dev|--development)
                DEV_MODE=true
                DEBUG_MODE=true
                ;;
            --check)
                CHECK_ONLY=true
                ;;
            --stop)
                STOP_ONLY=true
                ;;
            --status)
                STATUS_ONLY=true
                ;;
            --logs)
                LOGS_ONLY=true
                ;;
            --help|-h)
                show_banner
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $arg"
                show_help
                exit 1
                ;;
        esac
    done
    
    show_banner
    
    if [ "$STATUS_ONLY" = "true" ]; then
        show_status
        exit 0
    fi
    
    if [ "$LOGS_ONLY" = "true" ]; then
        show_logs
        exit 0
    fi
    
    if [ "$STOP_ONLY" = "true" ]; then
        stop_processes
        exit 0
    fi
    
    setup_directories
    
    if ! check_requirements; then
        if [ "$CHECK_ONLY" = "true" ]; then
            exit 1
        fi
        log_info "Some ports are in use. Use --stop to stop existing processes."
        exit 1
    fi
    
    if [ "$CHECK_ONLY" = "true" ]; then
        log_success "All system requirements met"
        exit 0
    fi
    
    if [ "$SETUP_FLAG" = "true" ]; then
        install_dependencies
    fi
    
    cache_models
    stop_processes
    trap cleanup SIGINT SIGTERM
    
    if [ "$FRONTEND_ONLY" != "true" ]; then
        if ! start_backend; then
            exit 1
        fi
    fi
    
    if [ "$BACKEND_ONLY" != "true" ]; then
        if ! start_frontend; then
            if [ "$FRONTEND_ONLY" != "true" ]; then
                cleanup
            fi
            exit 1
        fi
    fi
    
    echo ""
    echo -e "${GREEN}🎉 GödelOS v0.2 Beta is now running!${NC}"
    echo -e "${GREEN}====================================${NC}"
    show_status
    
    if [ "$DEV_MODE" = "true" ]; then
        log_info "Development mode: Backend will auto-reload on changes"
    fi
    
    echo -e "${YELLOW}💡 Tip: Open http://localhost:$FRONTEND_PORT in your browser${NC}"
    echo -e "${YELLOW}🛑 Press Ctrl+C to stop the system${NC}"
    echo ""
    
    log_info "System monitoring active..."
    while true; do
        sleep 5
        if [ "$FRONTEND_ONLY" != "true" ] && ! kill -0 "$BACKEND_PID" 2>/dev/null; then
            log_error "Backend server stopped unexpectedly"
            log_info "Check logs: tail -f $LOGS_DIR/backend.log"
            cleanup
        fi
        if [ "$BACKEND_ONLY" != "true" ] && ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
            log_error "Frontend server stopped unexpectedly"
            log_info "Check logs: tail -f $LOGS_DIR/frontend.log"
            cleanup
        fi
    done
}

main "$@"
