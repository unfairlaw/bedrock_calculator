#!/bin/bash

# AWS Cost Agent - Startup Script

echo "======================================"
echo "AWS Cost Agent - Web Interface"
echo "======================================"
echo ""

# Check if Flask is installed
python3 -c "import flask" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "📦 Installing dependencies..."
    echo ""
    pip3 install --break-system-packages Flask flask-cors 2>&1 | grep -v "WARNING"
    echo ""
fi

# Create necessary directories
mkdir -p static/css static/js templates

echo "✓ Dependencies installed"
echo "✓ Directories created"
echo ""
echo "🚀 Starting Flask server..."
echo ""
echo "Open your browser to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "======================================"
echo ""

# Run the Flask app
python3 app.py
