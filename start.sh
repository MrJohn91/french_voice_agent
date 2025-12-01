#!/bin/bash

echo "🇫🇷 French Voice Agent - Starting..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please copy .env.example to .env and configure your API keys"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  Warning: FFmpeg not found. Install with: brew install ffmpeg"
fi

# Start the agent
echo ""
echo "✅ Starting French Voice Agent..."
echo "🎤 Agent will be ready for French conversations"
echo "📞 Connect via LiveKit Playground: https://agents-playground.livekit.io"
echo ""

python agent/voice_agent.py dev
