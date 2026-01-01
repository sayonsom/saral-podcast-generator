#!/bin/bash
#
# Start script for Energy Debates Podcast Generator
# Starts both backend (FastAPI) and frontend (Next.js)
#

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  Energy Debates Podcast Generator   ${NC}"
echo -e "${GREEN}=====================================${NC}"
echo

# Check for .env file
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create a .env file with your API keys."
    exit 1
fi

# Create PID file directory
mkdir -p "$PROJECT_DIR/.pids"

# Function to check if a port is in use
port_in_use() {
    lsof -i :"$1" >/dev/null 2>&1
}

# Start Backend
echo -e "${YELLOW}Starting Backend (FastAPI on port 8000)...${NC}"
cd "$BACKEND_DIR"

# Activate virtual environment if exists, otherwise create it
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt -q
fi

# Check if port 8000 is in use
if port_in_use 8000; then
    echo -e "${RED}Port 8000 is already in use. Backend may already be running.${NC}"
else
    # Start uvicorn in background
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > "$PROJECT_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$PROJECT_DIR/.pids/backend.pid"
    echo -e "${GREEN}Backend started (PID: $BACKEND_PID)${NC}"
fi

# Start Frontend
echo -e "${YELLOW}Starting Frontend (Next.js on port 3000)...${NC}"
cd "$FRONTEND_DIR"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Check if port 3000 is in use
if port_in_use 3000; then
    echo -e "${RED}Port 3000 is already in use. Frontend may already be running.${NC}"
else
    # Start Next.js in background
    nohup npm run dev > "$PROJECT_DIR/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$PROJECT_DIR/.pids/frontend.pid"
    echo -e "${GREEN}Frontend started (PID: $FRONTEND_PID)${NC}"
fi

echo
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  Services Started Successfully!     ${NC}"
echo -e "${GREEN}=====================================${NC}"
echo
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "  API Docs: http://localhost:8000/docs"
echo
echo "Logs:"
echo "  Backend:  $PROJECT_DIR/backend.log"
echo "  Frontend: $PROJECT_DIR/frontend.log"
echo
echo -e "Run ${YELLOW}./teardown.sh${NC} to stop all services."
