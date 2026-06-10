@echo off
echo ===========================================
echo   VELUGU - Telugu AI Companion for Elderly
echo ===========================================
echo.

REM Install dependencies
echo [1/3] Installing dependencies...
pip install -r requirements.txt --quiet

REM Start Flask backend in background
echo [2/3] Starting Flask backend...
start "Velugu Backend" /min python backend\app.py

REM Wait 3 seconds for Flask to start
timeout /t 3 /nobreak > nul

REM Start Streamlit frontend
echo [3/3] Starting Streamlit frontend...
echo.
echo Open your browser at: http://localhost:8501
echo.
streamlit run frontend\app.py --server.port 8501