#!/usr/bin/env bash
set -e

echo "🔧 Setting up environment..."

# Load environment variables
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "⚠️ .env file not found. Make sure to create one with necessary variables."
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Optional: Run database migrations or setup
# echo "🗄️ Setting up database..."
# python apps_storage_db.py --init

# Optional: Start background jobs or schedulers
# echo "⏱️ Starting scheduler..."
# python apps_workflow_scheduler.py &

# Optional: Start telephony services
# echo "📞 Starting telephony gateway..."
# python apps_telephony_voice_gateway.py &

# Start the API server
echo "🚀 Launching API server..."
uvicorn apps_api_server:app --host 0.0.0.0 --port 8080
