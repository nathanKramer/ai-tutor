#!/bin/bash

echo "🤖 Setting up AI Pair Programming Tutor..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your OpenAI API key"
fi

echo "✅ Setup complete!"
echo ""
echo "To run the AI tutor:"
echo "1. source venv/bin/activate"
echo "2. python3 main.py"
echo ""
echo "Make sure to:"
echo "- Add your OpenAI API key to the .env file"
echo "- Have a microphone connected"
echo "- Have speakers/headphones for audio output"