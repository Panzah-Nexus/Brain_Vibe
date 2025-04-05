#!/bin/bash

# Set up a trap to kill background processes when the script exits
trap "kill 0" EXIT

# Start backend
echo "Starting backend server..."
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait a bit for the backend to initialize
sleep 2

# Start frontend
echo "Starting frontend server..."
cd ../frontend
npm install
npm start &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

# Wait for either process to exit
wait $BACKEND_PID $FRONTEND_PID 