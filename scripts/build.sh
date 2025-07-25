#!/bin/bash

# AI Tutor Build Script
echo "🚀 Building AI Tutor..."

# Change to project root directory (parent of scripts/)
cd "$(dirname "$0")/.."

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not detected"
    echo "   Activating virtual environment..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "✓ Virtual environment activated"
    else
        echo "❌ Virtual environment not found. Run setup.sh first."
        exit 1
    fi
fi

# Install PyInstaller if not already installed
if ! venv/bin/python -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Installing PyInstaller..."
    venv/bin/pip install pyinstaller
fi

# Run the Python build script with virtual environment python
venv/bin/python scripts/build.py

echo "✅ Build complete! Check the dist/ directory."