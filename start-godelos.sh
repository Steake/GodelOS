#!/bin/bash

# GödelOS Unified Startup System
# Complete system launcher for backend and frontend
# Version: 0.2 Beta

set -e

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=${GODELOS_BACKEND_PORT:-8000}
FRONTEND_PORT=${GODELOS_FRONTEND_PORT:-3000}
BACKEND_HOST=${GODELOS_BACKEND_HOST:-0.0.0.0}
FRONTEND_HOST=${GODELOS_FRONTEND_HOST:-0.0.0.0}
FRONTEND_TYPE=${GODELOS_FRONTEND_TYPE:-auto}

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_HTML_DIR="$SCRIPT_DIR/godelos-frontend"
FRONTEND_SVELTE_DIR="$SCRIPT_DIR/svelte-frontend"
LOGS_DIR="$SCRIPT_DIR/logs"

# Auto-detect frontend type
FRONTEND_DIR=""
DETECTED_FRONTEND_TYPE=""

# PID storage
BACKEND_PID=""
FRONTEND_PID=""

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
    echo "  --html-frontend        Force use HTML frontend (godelos-frontend)"
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
    echo "  GODELOS_FRONTEND_PORT=3000   Frontend port"
    echo "  GODELOS_BACKEND_HOST=0.0.0.0 Backend host"
    echo "  GODELOS_FRONTEND_HOST=0.0.0.0 Frontend host"
    echo "  GODELOS_FRONTEND_TYPE=auto   Frontend type (auto, html, svelte)"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 --setup                   # First-time setup and start"
    echo "  $0 --dev                     # Development mode"
    echo "  $0 --backend-only --debug    # Debug backend only"
    echo "  GODELOS_BACKEND_PORT=8080 $0 # Custom backend port"
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
    if [ "$FRONTEND_TYPE" = "html" ] || [ "$FRONTEND_TYPE" = "HTML" ]; then
        FRONTEND_DIR="$FRONTEND_HTML_DIR"
        DETECTED_FRONTEND_TYPE="html"
    elif [ "$FRONTEND_TYPE" = "svelte" ] || [ "$FRONTEND_TYPE" = "SVELTE" ]; then
        FRONTEND_DIR="$FRONTEND_SVELTE_DIR"
        DETECTED_FRONTEND_TYPE="svelte"
    else
        # Auto-detect based on what's available and preferred
        if [ -d "$FRONTEND_SVELTE_DIR" ] && [ -f "$FRONTEND_SVELTE_DIR/package.json" ]; then
            # Check if node_modules exists (dependencies installed)
            if [ -d "$FRONTEND_SVELTE_DIR/node_modules" ] || command_exists npm; then
                FRONTEND_DIR="$FRONTEND_SVELTE_DIR"
                DETECTED_FRONTEND_TYPE="svelte"
            fi
        fi
        
        # Fallback to HTML frontend
        if [ -z "$FRONTEND_DIR" ] && [ -d "$FRONTEND_HTML_DIR" ] && [ -f "$FRONTEND_HTML_DIR/index.html" ]; then
            FRONTEND_DIR="$FRONTEND_HTML_DIR"
            DETECTED_FRONTEND_TYPE="html"
        fi
        
        # Final fallback
        if [ -z "$FRONTEND_DIR" ]; then
            if [ -d "$FRONTEND_SVELTE_DIR" ]; then
                FRONTEND_DIR="$FRONTEND_SVELTE_DIR"
                DETECTED_FRONTEND_TYPE="svelte"
            elif [ -d "$FRONTEND_HTML_DIR" ]; then
                FRONTEND_DIR="$FRONTEND_HTML_DIR"
                DETECTED_FRONTEND_TYPE="html"
            fi
        fi
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
        # Fallback: try to connect
        timeout 1 bash -c "</dev/tcp/localhost/$port" >/dev/null 2>&1
    fi
}

# Create necessary directories
setup_directories() {
    log_step "Setting up directories..."
    mkdir -p "$LOGS_DIR"
    mkdir -p "$BACKEND_DIR/logs"
    mkdir -p "$BACKEND_DIR/storage"
    mkdir -p "$SCRIPT_DIR/knowledge_storage"
    mkdir -p "$SCRIPT_DIR/meta_knowledge_store"
    log_success "Directories created"
}

# Check system requirements
check_requirements() {
    log_step "Checking system requirements..."
    
    # Check Python
    if ! command_exists python3; then
        log_error "Python 3 is required but not found"
        log_info "Please install Python 3.8+ and try again"
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    log_success "Python $python_version found"
    
    # Check required directories
    if [ ! -d "$BACKEND_DIR" ]; then
        log_error "Backend directory not found: $BACKEND_DIR"
        log_info "Please run this script from the GödelOS root directory"
        exit 1
    fi
    
    if [ ! -f "$BACKEND_DIR/main.py" ]; then
        log_error "Backend main.py not found"
        exit 1
    fi
    
    # Detect frontend
    detect_frontend
    
    if [ -z "$FRONTEND_DIR" ] || [ ! -d "$FRONTEND_DIR" ]; then
        log_error "No suitable frontend found"
        log_info "Available options:"
        [ -d "$FRONTEND_HTML_DIR" ] && log_info "  - HTML Frontend: $FRONTEND_HTML_DIR"
        [ -d "$FRONTEND_SVELTE_DIR" ] && log_info "  - Svelte Frontend: $FRONTEND_SVELTE_DIR"
        exit 1
    fi
    
    # Validate frontend based on type
    if [ "$DETECTED_FRONTEND_TYPE" = "html" ]; then
        if [ ! -f "$FRONTEND_DIR/index.html" ]; then
            log_error "HTML frontend index.html not found"
            exit 1
        fi
    elif [ "$DETECTED_FRONTEND_TYPE" = "svelte" ]; then
        if [ ! -f "$FRONTEND_DIR/package.json" ]; then
            log_error "Svelte frontend package.json not found"
            exit 1
        fi
    fi
    
    log_success "All required files found"
    log_success "Frontend type: $DETECTED_FRONTEND_TYPE ($FRONTEND_DIR)"
    
    # Check ports
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
    
    # Detect frontend first
    detect_frontend
    
    # Backend dependencies
    if [ ! -d "$BACKEND_DIR/venv" ] && [ -z "$VIRTUAL_ENV" ]; then
        log_step "Creating Python virtual environment..."
        cd "$BACKEND_DIR"
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        log_success "Python virtual environment created"
    fi
    
    # Install Python dependencies
    if [ -f "$BACKEND_DIR/requirements.txt" ]; then
        log_step "Installing Python dependencies..."
        if [ -d "$BACKEND_DIR/venv" ] && [ -z "$VIRTUAL_ENV" ]; then
            source "$BACKEND_DIR/venv/bin/activate"
        fi
        pip install -r "$BACKEND_DIR/requirements.txt"
        log_success "Python dependencies installed"
    fi
    
    # Frontend dependencies
    if [ "$DETECTED_FRONTEND_TYPE" = "svelte" ]; then
        log_step "Installing Svelte frontend dependencies..."
        if ! command_exists npm; then
            log_warning "npm not found - Svelte frontend requires Node.js and npm"
            log_info "Please install Node.js from https://nodejs.org/"
            log_info "Falling back to HTML frontend"
            FRONTEND_DIR="$FRONTEND_HTML_DIR"
            DETECTED_FRONTEND_TYPE="html"
        else
            cd "$FRONTEND_DIR"
            npm install
            log_success "Svelte dependencies installed"
            cd "$SCRIPT_DIR"
        fi
    fi
    
    # Check critical Python dependencies
    python3 -c "
import sys
missing = []
required = ['fastapi', 'uvicorn', 'pydantic']
for module in required:
    try:
        __import__(module)
    except ImportError:
        missing.append(module)

if missing:
    print(f'❌ Missing critical dependencies: {missing}')
    sys.exit(1)
else:
    print('✅ All critical dependencies available')
" || exit 1
}

# Stop existing processes
stop_processes() {
    log_step "Stopping existing GödelOS processes..."
    
    # Kill by PID files
    if [ -f "$LOGS_DIR/backend.pid" ]; then
        local pid=$(cat "$LOGS_DIR/backend.pid")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            log_success "Stopped backend process (PID: $pid)"
        fi
        rm -f "$LOGS_DIR/backend.pid"
    fi
    
    if [ -f "$LOGS_DIR/frontend.pid" ]; then
        local pid=$(cat "$LOGS_DIR/frontend.pid")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            log_success "Stopped frontend process (PID: $pid)"
        fi
        rm -f "$LOGS_DIR/frontend.pid"
    fi
    
    # Kill by process name (fallback)
    pkill -f "uvicorn.*main:app" 2>/dev/null && log_success "Stopped uvicorn processes"
    pkill -f "python.*http.server.*$FRONTEND_PORT" 2>/dev/null && log_success "Stopped frontend server"
    
    # Wait a moment for cleanup
    sleep 1
    
    log_success "All existing processes stopped"
}

# Start backend
start_backend() {
    log_step "Starting backend server on port $BACKEND_PORT..."
    
    cd "$BACKEND_DIR"
    
    # Activate virtual environment if it exists
    if [ -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
        source venv/bin/activate
    fi
    
    # Prepare startup command
    local cmd="python3 -m uvicorn main:app --host $BACKEND_HOST --port $BACKEND_PORT"
    
    if [ "$DEBUG_MODE" = "true" ]; then
        cmd="$cmd --reload --log-level debug"
    fi
    
    # Start backend
    $cmd > "$LOGS_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    
    echo $BACKEND_PID > "$LOGS_DIR/backend.pid"
    
    cd "$SCRIPT_DIR"
    
    # Wait for backend to start
    log_step "Waiting for backend initialization..."
    local attempts=0
    local max_attempts=30
    
    while [ $attempts -lt $max_attempts ]; do
        if port_in_use $BACKEND_PORT; then
            log_success "Backend server started (PID: $BACKEND_PID)"
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
        if [ $((attempts % 5)) -eq 0 ]; then
            echo -ne "${YELLOW}  Waiting... ${attempts}/${max_attempts}\r${NC}"
        fi
    done
    
    log_error "Backend failed to start within ${max_attempts} seconds"
    log_info "Check logs: tail -f $LOGS_DIR/backend.log"
    return 1
}

# Configure frontend for backend connection
configure_frontend() {
    if [ "$DETECTED_FRONTEND_TYPE" = "svelte" ]; then
        log_step "Configuring Svelte frontend for backend port $BACKEND_PORT..."
        
        # Create .env file for Vite
        cat > "$FRONTEND_DIR/.env" << EOF
VITE_BACKEND_PORT=$BACKEND_PORT
VITE_BACKEND_HOST=$BACKEND_HOST
VITE_FRONTEND_PORT=$FRONTEND_PORT
EOF

        # Create a public config file that can be accessed at runtime
        mkdir -p "$FRONTEND_DIR/public"
        cat > "$FRONTEND_DIR/public/config.js" << EOF
// GödelOS Frontend Configuration
window.GODELOS_BACKEND_PORT = '$BACKEND_PORT';
window.GODELOS_BACKEND_HOST = '$BACKEND_HOST';
window.GODELOS_FRONTEND_PORT = '$FRONTEND_PORT';
console.log('🔧 GödelOS Config Loaded - Backend: http://' + window.GODELOS_BACKEND_HOST + ':' + window.GODELOS_BACKEND_PORT);
EOF
        
        log_success "Frontend configured for backend at $BACKEND_HOST:$BACKEND_PORT"
    fi
}

# Start frontend
start_frontend() {
    # Detect frontend type if not already done
    if [ -z "$DETECTED_FRONTEND_TYPE" ]; then
        detect_frontend
    fi
    
    # Configure frontend for backend connection
    configure_frontend
    
    log_step "Starting $DETECTED_FRONTEND_TYPE frontend server on port $FRONTEND_PORT..."
    
    cd "$FRONTEND_DIR"
    
    if [ "$DETECTED_FRONTEND_TYPE" = "svelte" ]; then
        # Start Svelte dev server
        if [ "$DEBUG_MODE" = "true" ] || [ "$DEV_MODE" = "true" ]; then
            VITE_BACKEND_PORT=$BACKEND_PORT npm run dev -- --host $FRONTEND_HOST --port $FRONTEND_PORT > "$LOGS_DIR/frontend.log" 2>&1 &
        else
            # Build and serve for production
            log_step "Building Svelte frontend with backend config..."
            VITE_BACKEND_PORT=$BACKEND_PORT npm run build
            log_step "Starting Svelte preview server..."
            npm run preview -- --host $FRONTEND_HOST --port $FRONTEND_PORT > "$LOGS_DIR/frontend.log" 2>&1 &
        fi
        FRONTEND_PID=$!
    else
        # Start simple HTTP server for HTML frontend
        python3 -m http.server $FRONTEND_PORT --bind $FRONTEND_HOST > "$LOGS_DIR/frontend.log" 2>&1 &
        FRONTEND_PID=$!
    fi
    
    echo $FRONTEND_PID > "$LOGS_DIR/frontend.pid"
    
    cd "$SCRIPT_DIR"
    
    # Wait for frontend to start
    local attempts=0
    local max_attempts=15
    
    while [ $attempts -lt $max_attempts ]; do
        if port_in_use $FRONTEND_PORT; then
            log_success "$DETECTED_FRONTEND_TYPE frontend server started (PID: $FRONTEND_PID)"
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
        if [ $((attempts % 3)) -eq 0 ]; then
            echo -ne "${YELLOW}  Waiting for $DETECTED_FRONTEND_TYPE frontend... ${attempts}/${max_attempts}\r${NC}"
        fi
    done
    
    log_error "$DETECTED_FRONTEND_TYPE frontend failed to start within ${max_attempts} seconds"
    log_info "Check logs: tail -f $LOGS_DIR/frontend.log"
    return 1
}

# Show status
show_status() {
    echo -e "${BLUE}📊 GödelOS System Status${NC}"
    echo -e "${BLUE}========================${NC}"
    echo ""
    
    # Check backend
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
    
    # Check frontend
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
    echo -e "   WebSocket: ${CYAN}ws://localhost:$BACKEND_PORT/ws/cognitive-stream${NC}"
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
    
    if [ ! -z "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID"
        log_success "Backend server stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID"
        log_success "Frontend server stopped"
    fi
    
    # Clean up PID files
    rm -f "$LOGS_DIR/backend.pid" "$LOGS_DIR/frontend.pid"
    
    echo -e "${PURPLE}👋 GödelOS system shutdown complete${NC}"
    exit 0
}

# Main execution logic
main() {
    # Parse arguments
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
            --html-frontend)
                FRONTEND_TYPE="html"
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
    
    # Show banner
    show_banner
    
    # Handle special modes
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
    
    # Setup directories
    setup_directories
    
    # Check requirements
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
    
    # Install dependencies if needed
    if [ "$SETUP_FLAG" = "true" ]; then
        install_dependencies
    fi
    
    # Stop existing processes
    stop_processes
    
    # Set up signal handlers
    trap cleanup SIGINT SIGTERM
    
    # Start services
    if [ "$FRONTEND_ONLY" != "true" ]; then
        if ! start_backend; then
            exit 1
        fi
    fi
    
    if [ "$BACKEND_ONLY" != "true" ]; then
        if ! start_frontend; then
            # If backend was started, clean it up
            if [ "$FRONTEND_ONLY" != "true" ]; then
                cleanup
            fi
            exit 1
        fi
    fi
    
    # Show success message
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
    
    # Monitor system
    log_info "System monitoring active..."
    while true; do
        sleep 5
        
        # Check if processes are still running
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

# Run main function
main "$@"