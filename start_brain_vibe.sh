#!/bin/bash

# Brain Vibe Startup Script
# Compatible with Linux, macOS, and Windows (WSL)

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Set up trap to kill all background processes when the script exits
trap cleanup EXIT INT TERM

cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    # Kill all child processes
    pkill -P $$
    # Additional cleanup as needed
    echo -e "${GREEN}All services stopped.${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if we're running in WSL
is_wsl() {
    grep -q "microsoft" /proc/version 2>/dev/null
    return $?
}

# Function to open a browser (WSL-aware)
open_browser() {
    local url=$1
    
    if is_wsl; then
        echo -e "${BLUE}Opening browser in Windows...${NC}"
        # Try to use Windows' default browser
        powershell.exe -c "start $url" >/dev/null 2>&1 || \
        cmd.exe /c "start $url" >/dev/null 2>&1
    else
        echo -e "${BLUE}Opening browser...${NC}"
        # Try different open commands based on the OS
        if command_exists xdg-open; then
            xdg-open "$url" >/dev/null 2>&1
        elif command_exists open; then
            open "$url" >/dev/null 2>&1
        elif command_exists firefox; then
            firefox "$url" >/dev/null 2>&1
        elif command_exists google-chrome; then
            google-chrome "$url" >/dev/null 2>&1
        else
            echo -e "${YELLOW}Couldn't open browser automatically. Please open $url manually.${NC}"
        fi
    fi
}

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Starting Brain Vibe Application  ${NC}"
echo -e "${BLUE}============================================${NC}"

# Check Python version
if ! command_exists python3; then
    echo -e "${RED}Python 3 is required but not installed.${NC}"
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}Using Python version: $python_version${NC}"

# Check for npm
if ! command_exists npm; then
    echo -e "${RED}npm is required but not installed.${NC}"
    exit 1
fi

npm_version=$(npm --version)
echo -e "${GREEN}Using npm version: $npm_version${NC}"

# Check if .env file exists, create if not
if [ ! -f "$SCRIPT_DIR/backend/.env" ]; then
    echo -e "${YELLOW}Creating .env file from example...${NC}"
    if [ -f "$SCRIPT_DIR/backend/.env.example" ]; then
        cp "$SCRIPT_DIR/backend/.env.example" "$SCRIPT_DIR/backend/.env"
        echo -e "${YELLOW}Please edit backend/.env file to add your Gemini API key${NC}"
    else
        echo -e "${RED}No .env.example file found. Creating empty .env file...${NC}"
        echo "# Gemini API Key - Add your key here" > "$SCRIPT_DIR/backend/.env"
        echo "GEMINI_API_KEY=" >> "$SCRIPT_DIR/backend/.env"
        echo -e "${YELLOW}Please add your Gemini API key to backend/.env${NC}"
    fi
fi

# Check if data directory exists, create if not
if [ ! -d "$SCRIPT_DIR/backend/data" ]; then
    echo -e "${YELLOW}Creating data directory...${NC}"
    mkdir -p "$SCRIPT_DIR/backend/data"
fi

echo -e "\n${BLUE}Setting up backend...${NC}"
cd "$SCRIPT_DIR/backend"

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment.${NC}"
        exit 1
    fi
fi

echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to activate virtual environment.${NC}"
    exit 1
fi

echo -e "${YELLOW}Installing backend dependencies...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install backend dependencies.${NC}"
    exit 1
fi

# Start the backend
echo -e "\n${GREEN}Starting backend server...${NC}"
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Check if backend started successfully
sleep 3
if ! ps -p $BACKEND_PID > /dev/null; then
    echo -e "${RED}Backend failed to start. Check the error messages above.${NC}"
    exit 1
fi
echo -e "${GREEN}Backend running with PID: $BACKEND_PID${NC}"

# Set up frontend
echo -e "\n${BLUE}Setting up frontend...${NC}"
cd "$SCRIPT_DIR/frontend"

echo -e "${YELLOW}Installing frontend dependencies...${NC}"
npm install
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install frontend dependencies.${NC}"
    kill $BACKEND_PID
    exit 1
fi

# Start the frontend
echo -e "\n${GREEN}Starting frontend server...${NC}"
npm start &
FRONTEND_PID=$!

# Check if frontend started successfully
sleep 5
if ! ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${RED}Frontend failed to start. Check the error messages above.${NC}"
    kill $BACKEND_PID
    exit 1
fi
echo -e "${GREEN}Frontend running with PID: $FRONTEND_PID${NC}"

# Display access information
echo -e "\n${BLUE}============================================${NC}"
echo -e "${GREEN}Brain Vibe is now running!${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "Frontend: ${YELLOW}http://localhost:3000${NC}"
echo -e "Backend API: ${YELLOW}http://localhost:8000${NC}"
echo -e "API Documentation: ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "${BLUE}============================================${NC}"

# Determine if we should open a browser automatically
if is_wsl; then
    # In WSL, ask before opening the browser as it might be unexpected
    echo -e "${YELLOW}Running in WSL. Would you like to open the frontend in your Windows browser? (y/n)${NC}"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        open_browser "http://localhost:3000"
    fi
else
    # On a regular Linux system, just open the browser
    open_browser "http://localhost:3000"
fi

echo -e "\n${YELLOW}Press Ctrl+C to stop all services.${NC}"

# Wait for processes to complete (or more likely, for the user to press Ctrl+C)
wait $BACKEND_PID $FRONTEND_PID 