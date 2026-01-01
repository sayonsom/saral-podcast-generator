#!/bin/bash
#
# Teardown script for Energy Debates Podcast Generator
# Stops all running services
#

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDS_DIR="$PROJECT_DIR/.pids"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=====================================${NC}"
echo -e "${YELLOW}  Stopping Podcast Generator         ${NC}"
echo -e "${YELLOW}=====================================${NC}"
echo

# Function to stop a service by PID file
stop_service() {
    local name=$1
    local pid_file="$PIDS_DIR/$2"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "Stopping $name (PID: $pid)..."
            kill "$pid" 2>/dev/null
            # Wait a moment for graceful shutdown
            sleep 1
            # Force kill if still running
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid" 2>/dev/null
            fi
            echo -e "${GREEN}$name stopped.${NC}"
        else
            echo -e "${YELLOW}$name process not running (stale PID file).${NC}"
        fi
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}$name PID file not found.${NC}"
    fi
}

# Stop Backend
stop_service "Backend" "backend.pid"

# Stop Frontend
stop_service "Frontend" "frontend.pid"

# Also try to kill any remaining processes on the ports
echo
echo "Checking for remaining processes on ports..."

# Kill anything on port 8000 (backend)
BACKEND_PIDS=$(lsof -ti :8000 2>/dev/null)
if [ -n "$BACKEND_PIDS" ]; then
    echo -e "Killing remaining processes on port 8000..."
    echo "$BACKEND_PIDS" | xargs kill -9 2>/dev/null
fi

# Kill anything on port 3000 (frontend)
FRONTEND_PIDS=$(lsof -ti :3000 2>/dev/null)
if [ -n "$FRONTEND_PIDS" ]; then
    echo -e "Killing remaining processes on port 3000..."
    echo "$FRONTEND_PIDS" | xargs kill -9 2>/dev/null
fi

# Clean up PID directory
rm -rf "$PIDS_DIR"

echo
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  All Services Stopped               ${NC}"
echo -e "${GREEN}=====================================${NC}"
