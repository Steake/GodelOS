#!/bin/bash

# GödelOS Complete System Stop Script
# Gracefully shuts down backend and frontend servers

echo "🛑 Stopping GödelOS Complete System..."
echo "===================================="

# Function to stop process by PID file
stop_service() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🔄 Stopping $service_name (PID: $pid)..."
            kill "$pid"
            
            # Wait up to 10 seconds for graceful shutdown
            local count=0
            while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚠️  Force stopping $service_name..."
                kill -9 "$pid" 2>/dev/null
            fi
            
            echo "✅ $service_name stopped"
        else
            echo "ℹ️  $service_name was not running"
        fi
        rm -f "$pid_file"
    else
        echo "ℹ️  No $service_name PID file found"
    fi
}

# Stop services using PID files
if [ -d "logs" ]; then
    stop_service "Backend server" "logs/backend.pid"
    stop_service "Frontend server" "logs/frontend.pid"
else
    echo "ℹ️  No logs directory found"
fi

# Also try to stop by port (backup method)
echo "🔍 Checking for remaining processes on ports 8000 and 3000..."

# Stop any process on port 8000 (backend)
backend_pids=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$backend_pids" ]; then
    echo "🔄 Found processes on port 8000, stopping..."
    echo "$backend_pids" | xargs kill 2>/dev/null
    sleep 2
    # Force kill if still there
    backend_pids=$(lsof -ti:8000 2>/dev/null)
    if [ ! -z "$backend_pids" ]; then
        echo "$backend_pids" | xargs kill -9 2>/dev/null
    fi
    echo "✅ Port 8000 cleared"
fi

# Stop any process on port 3000 (frontend)
frontend_pids=$(lsof -ti:3000 2>/dev/null)
if [ ! -z "$frontend_pids" ]; then
    echo "🔄 Found processes on port 3000, stopping..."
    echo "$frontend_pids" | xargs kill 2>/dev/null
    sleep 2
    # Force kill if still there
    frontend_pids=$(lsof -ti:3000 2>/dev/null)
    if [ ! -z "$frontend_pids" ]; then
        echo "$frontend_pids" | xargs kill -9 2>/dev/null
    fi
    echo "✅ Port 3000 cleared"
fi

# Final verification
echo "🔍 Final verification..."
if lsof -ti:8000 >/dev/null 2>&1; then
    echo "⚠️  Warning: Something is still running on port 8000"
else
    echo "✅ Port 8000 is free"
fi

if lsof -ti:3000 >/dev/null 2>&1; then
    echo "⚠️  Warning: Something is still running on port 3000"
else
    echo "✅ Port 3000 is free"
fi

echo ""
echo "🎉 GödelOS system shutdown complete!"
echo "=================================="
echo "💡 To start the system again, run: ./start-godelos-complete.sh"
echo ""