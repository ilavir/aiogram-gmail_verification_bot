#!/bin/bash

# Gmail Verification Bot - Production Deployment Script

set -e

echo "🚀 Deploying Gmail Verification Bot..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Please copy .env.production to .env and configure it:"
    echo "   cp .env.production .env"
    echo "   nano .env"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose (modern version) is available
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose (modern version) is not available."
    echo "Please update Docker to a version that includes 'docker compose' command."
    exit 1
fi

# Stop existing container if running
echo "🛑 Stopping existing containers..."
docker compose down || true

# Build and start the service
echo "🔨 Building and starting Gmail Verification Bot..."
docker compose up --build -d

# Show status
echo "📊 Container status:"
docker compose ps

# Show logs
echo "📋 Recent logs:"
docker compose logs --tail=20 gmail-bot

echo ""
echo "✅ Gmail Verification Bot deployed successfully!"
echo ""
echo "📋 Useful commands:"
echo "   View logs:     docker compose logs -f gmail-bot"
echo "   Stop bot:      docker compose down"
echo "   Restart bot:   docker compose restart gmail-bot"
echo "   Update bot:    ./deploy.sh"
echo "   Shell access:  docker compose exec gmail-bot /bin/bash"
echo ""
echo "🔍 First-time setup:"
echo "   The bot will open a browser for Gmail OAuth on first run."
echo "   Check logs with: docker compose logs -f gmail-bot"
