#!/bin/bash
# Stop the Social Hub backend server

ps aux | grep 'run.py\|python.*server\|uvicorn' | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true
echo "All servers stopped"

