#!/bin/bash
echo "==========================================="
echo "  VELUGU - Telugu AI Companion for Elderly"
echo "==========================================="
echo

# Install dependencies
echo "[1/3] Installing dependencies..."
pip install -r requirements.txt -q

# Start Flask backend in background
echo "[2/3] Starting Flask backend on port 5000..."
python backend/app.py &
FLASK_PID=$!

# Wait for Flask to start
sleep 3

# Start Streamlit
echo "[3/3] Starting Streamlit frontend..."
echo
echo "Open your browser at: http://localhost:8501"
echo "Press Ctrl+C to stop everything."
echo

streamlit run frontend/app.py --server.port 8501

# On exit, kill Flask too
kill $FLASK_PID 2>/dev/null