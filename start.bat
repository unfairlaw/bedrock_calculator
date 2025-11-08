@echo off
REM AWS Cost Agent - Windows Startup Script

echo ======================================
echo AWS Cost Agent - Web Interface
echo ======================================
echo.

REM Check if Flask is installed
python -c "import flask" 2>nul

if %errorlevel% neq 0 (
    echo Installing dependencies...
    echo.
    pip install Flask flask-cors
    echo.
)

REM Create necessary directories
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "templates" mkdir templates

echo Dependencies installed
echo Directories created
echo.
echo Starting Flask server...
echo.
echo Open your browser to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ======================================
echo.

REM Run the Flask app
python app.py
