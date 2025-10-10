#!/bin/bash
# Development script - Start both backend and frontend

echo "🚀 Starting Social Hub Development Environment..."
echo ""

# Start backend
echo "Starting backend server..."
cd "$(dirname "$0")/.."
python run.py > logs/server.log 2>&1 &
BACKEND_PID=$!
echo "✓ Backend started (PID: $BACKEND_PID) - Logs: logs/server.log"

# Wait for backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
  echo "✓ Backend is healthy at http://localhost:8000"
else
  echo "⚠ Backend may not be running properly. Check logs/server.log"
fi

echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: Will start on http://localhost:5173 (run 'npm run dev' in frontend/)"
echo ""
echo "To stop all servers, run: ./scripts/stop_server.sh"

