#!/bin/bash

# GödelOS Enhanced Cognitive Features Demo Startup Script
# This script starts the complete system and demonstrates all features

set -e

echo "🧠 GödelOS Enhanced Cognitive Features Demo"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to kill processes on a port
kill_port() {
    local port=$1
    print_info "Checking port $port..."
    if check_port $port; then
        print_warning "Port $port is in use, killing processes..."
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 2
        if check_port $port; then
            print_error "Failed to free port $port"
            return 1
        else
            print_status "Port $port is now free"
        fi
    else
        print_status "Port $port is available"
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    print_info "Waiting for $name to start..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            print_status "$name is running!"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$name failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Check environment
print_info "Checking environment..."

# Ensure we're in the right directory
if [ ! -f "backend/start_server.py" ]; then
    print_error "Please run this script from the GödelOS.md directory"
    exit 1
fi

# Check Python virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "Virtual environment not detected. Activating godel_venv..."
    if [ -f "godel_venv/bin/activate" ]; then
        source godel_venv/bin/activate
        print_status "Virtual environment activated"
    else
        print_error "Virtual environment not found. Please run: python -m venv godel_venv && source godel_venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
fi

print_status "Environment check completed"

# Step 1: Clean up any existing processes
print_info "Step 1: Cleaning up existing processes..."

# Kill any existing backend processes
pkill -f "start_server.py" 2>/dev/null || true
pkill -f "python.*backend" 2>/dev/null || true

# Clean up ports
kill_port 8000  # Backend
kill_port 5173  # Frontend

print_status "Cleanup completed"

# Step 2: Start Backend
print_info "Step 2: Starting Enhanced Cognitive Backend..."

# Start backend in background
python backend/start_server.py --debug > logs/backend_demo.log 2>&1 &
BACKEND_PID=$!

print_info "Backend started with PID: $BACKEND_PID"

# Wait for backend to be ready
if wait_for_service "http://localhost:8000/health" "Backend"; then
    print_status "Backend is ready!"
else
    print_error "Backend failed to start. Check logs/backend_demo.log"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Step 3: Test Enhanced Cognitive Features
print_info "Step 3: Testing Enhanced Cognitive Features..."

# Test enhanced cognitive API
print_info "Testing enhanced cognitive streaming status..."
STREAM_STATUS=$(curl -s http://localhost:8000/api/enhanced-cognitive/stream/status 2>/dev/null || echo "ERROR")

if echo "$STREAM_STATUS" | grep -q "stream_coordinator_available"; then
    print_status "Enhanced cognitive API is responding!"
    
    # Parse and display key metrics
    if echo "$STREAM_STATUS" | jq '.' > /dev/null 2>&1; then
        echo ""
        echo "📊 Enhanced Cognitive Status:"
        echo "$STREAM_STATUS" | jq -r '
            "   🔗 Stream Coordinator: " + (if .stream_coordinator_available then "✅ Available" else "❌ Not Available" end),
            "   🧠 Enhanced Metacognition: " + (if .enhanced_metacognition.is_running then "✅ Running" else "❌ Not Running" end),
            "   🤖 Autonomous Learning: " + (if .enhanced_metacognition.autonomous_learning.enabled then "✅ Enabled" else "❌ Disabled" end),
            "   📡 Cognitive Streaming: " + (if .enhanced_metacognition.cognitive_streaming.enabled then "✅ Enabled" else "❌ Disabled" end),
            "   🔄 Active Acquisitions: " + (.enhanced_metacognition.autonomous_learning.active_acquisitions | tostring),
            "   🕳️  Detected Gaps: " + (.enhanced_metacognition.autonomous_learning.detected_gaps | tostring),
            "   👥 Connected Clients: " + (.enhanced_metacognition.cognitive_streaming.connected_clients | tostring)
        '
    fi
else
    print_error "Enhanced cognitive API not responding properly"
    echo "Response: $STREAM_STATUS"
fi

# Step 4: Start Frontend
print_info "Step 4: Starting Svelte Frontend..."

# Check if frontend is already running
if check_port 5173; then
    print_warning "Frontend already running on port 5173"
else
    cd svelte-frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_info "Installing frontend dependencies..."
        npm install
    fi
    
    # Start frontend in background
    npm run dev > ../logs/frontend_demo.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    print_info "Frontend started with PID: $FRONTEND_PID"
    
    # Wait for frontend to be ready
    if wait_for_service "http://localhost:5173" "Frontend"; then
        print_status "Frontend is ready!"
    else
        print_error "Frontend failed to start. Check logs/frontend_demo.log"
        kill $FRONTEND_PID 2>/dev/null || true
    fi
fi

# Step 5: Demo Instructions
echo ""
echo "🌟 GödelOS Enhanced Cognitive Features Demo Ready!"
echo "================================================"
echo ""
echo "🔗 Access Points:"
echo "   • Backend API: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Frontend UI: http://localhost:5173"
echo ""
echo "🧠 Enhanced Cognitive Features:"
echo "   • Enhanced Cognitive Dashboard: Available in frontend navigation"
echo "   • Real-time WebSocket streaming: ws://localhost:8000/api/enhanced-cognitive/stream"
echo "   • Autonomous learning monitoring: /api/enhanced-cognitive/autonomous-learning/status"
echo "   • Stream of consciousness: /api/enhanced-cognitive/stream/status"
echo ""
echo "🎯 Demo Actions:"
echo "   1. Open http://localhost:5173 in your browser"
echo "   2. Navigate to 'Enhanced Cognitive Dashboard'"
echo "   3. Monitor real-time cognitive streaming"
echo "   4. Submit queries to see autonomous learning in action"
echo "   5. Observe knowledge gap detection and acquisition"
echo ""
echo "📊 Test Commands:"
echo "   • Check streaming status: curl http://localhost:8000/api/enhanced-cognitive/stream/status"
echo "   • Test query with learning: Use the frontend query interface"
echo "   • Monitor WebSocket: Use browser developer tools on frontend"
echo ""
echo "🔧 Logs:"
echo "   • Backend: logs/backend_demo.log"
echo "   • Frontend: logs/frontend_demo.log"
echo ""

# Step 6: Interactive demo
read -p "Press Enter to start interactive demo, or Ctrl+C to exit..."

# Run the Python demo script
print_info "Running interactive enhanced cognitive demo..."
python demo_enhanced_cognitive.py

echo ""
print_info "Demo completed! Services are still running."
print_info "Backend PID: $BACKEND_PID"
if [ ! -z "$FRONTEND_PID" ]; then
    print_info "Frontend PID: $FRONTEND_PID"
fi
print_info "Use 'kill $BACKEND_PID' and 'kill $FRONTEND_PID' to stop services"
