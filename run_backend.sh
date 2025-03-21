#!/bin/bash
# Script to run the FastAPI backend server

# Activate virtual environment
source backend/venv/bin/activate

# Set environment variables (if running locally)
export GEMINI_API_KEY=AIzaSyCfm2xX5Lsnpcq18u4Hzv3zbbXkEFbHn44

# Run the server
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
