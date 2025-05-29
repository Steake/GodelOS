#!/bin/bash

# GödelOS Complete System Startup Script
# Launches both backend and frontend servers for the integrated system

echo "🚀 Starting GödelOS Complete System..."
echo "======================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

# Check if required directories exist
if [ ! -d "backend" ]; then
    echo "❌ Error: backend directory not found."
    echo "Please run this script from the GödelOS root directory."
    exit 1
fi

if [ ! -d "godelos-frontend" ]; then
    echo "❌ Error: godelos-frontend directory not found."
    echo "Please run this script from the GödelOS root directory."
    exit 1
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Kill any existing backend or frontend processes
echo "🛑 Stopping any existing backend or frontend servers...
pkill -f 'uvicorn main:app' 2>/dev/null"
pkill -f 'python3 -m http.server' 2>/dev/null
echo "✅ Existing servers stopped"
# Ensure logs are empty
echo "" > logs/backend.log 2>&1
echo "" > logs/frontend.log 2>&1
# Ensure PID files are removed
rm -f logs/backend.pid logs/frontend.pid


# Check if ports are available
if check_port 8000; then
    echo "⚠️  Warning: Port 8000 is already in use (backend port)"
    echo "Please stop any existing backend server or use a different port."
    exit 1
fi

if check_port 3000; then
    echo "⚠️  Warning: Port 3000 is already in use (frontend port)"
    echo "Please stop any existing frontend server or use a different port."
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking Python dependencies..."
python3 -c "
import sys
missing = []
required = ['fastapi', 'uvicorn', 'pydantic', 'aiohttp', 'aiofiles', 'PyPDF2', 'docx', 'bs4']
for module in required:
    try:
        if module == 'docx':
            import docx
        elif module == 'bs4':
            import bs4
        else:
            __import__(module)
    except ImportError:
        missing.append(module)

if missing:
    print(f'Missing dependencies: {missing}')
    print('Run: pip install fastapi uvicorn pydantic aiohttp aiofiles PyPDF2 python-docx beautifulsoup4')
    sys.exit(1)
else:
    print('✅ All dependencies available')
"

if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Please install them and try again."
    exit 1
fi

# Create log directory
mkdir -p logs


# Start backend server in background
echo "🔧 Starting backend server on port 8000..."
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to fully initialize (GödelOS takes ~20-30 seconds)
echo "⏳ Waiting for backend initialization (this may take 20-30 seconds)..."
sleep 30

# Check if backend started successfully
if ! check_port 8000; then
    echo "❌ Failed to start backend server"
    echo "Check logs/backend.log for details"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Backend server started (PID: $BACKEND_PID)"

# Start frontend server in background
echo "🌐 Starting frontend server on port 3000..."
cd godelos-frontend
python3 -m http.server 3000 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 2

# Check if frontend started successfully
if ! check_port 3000; then
    echo "❌ Failed to start frontend server"
    echo "Check logs/frontend.log for details"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Frontend server started (PID: $FRONTEND_PID)"

# Save PIDs for cleanup
echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid

echo ""
echo "🎉 GödelOS Complete System is now running!"
echo "======================================"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Logs:"
echo "   Backend:  logs/backend.log"
echo "   Frontend: logs/frontend.log"
echo ""
echo "🛑 To stop the system, run: ./stop-godelos.sh"
echo "   Or press Ctrl+C to stop this script and kill servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down GödelOS system..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend server stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend server stopped"
    fi
    rm -f logs/backend.pid logs/frontend.pid
    echo "👋 GödelOS system shutdown complete"
    exit 0
}

# Set trap to cleanup on script termination
trap cleanup SIGINT SIGTERM

# Keep script running and show status
echo "💡 Tip: Open http://localhost:3000 in your browser to access GödelOS"
echo "🔄 System status monitoring... (Press Ctrl+C to stop)"
echo ""

# Monitor system health
while true; do
    sleep 10
    
    # Check if processes are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend server stopped unexpectedly"
        echo "Check logs/backend.log for details"
        cleanup
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend server stopped unexpectedly"
        echo "Check logs/frontend.log for details"
        cleanup
    fi
    
    # Show timestamp every minute
    if [ $(($(date +%s) % 60)) -eq 0 ]; then
        echo "⏰ $(date '+%H:%M:%S') - System running normally"
    fi
done