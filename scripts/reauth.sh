#!/bin/bash

# Gmail Re-authentication Script for Docker Production
# Usage: ./scripts/reauth.sh [AUTH_CODE]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔐 Gmail Docker Re-authentication Script"
echo "========================================"

# Check if running
if docker compose ps gmail-bot | grep -q "Up"; then
    echo "📦 Stopping Gmail bot container..."
    docker compose down
    echo "✅ Container stopped"
fi

# Method 1: Use provided auth code
if [ ! -z "$1" ]; then
    echo "🔑 Using provided authorization code..."
    
    # Set auth code and restart
    export GMAIL_AUTH_CODE="$1"
    echo "GMAIL_AUTH_CODE=$1" > .env.auth
    
    echo "🚀 Starting container with auth code..."
    docker compose --env-file .env --env-file .env.auth up -d
    
    # Wait for authentication
    echo "⏳ Waiting for authentication to complete..."
    sleep 10
    
    # Check logs for success
    if docker compose logs gmail-bot | grep -q "Gmail authentication successful"; then
        echo "✅ Authentication successful!"
        
        # Clean up auth code
        rm -f .env.auth
        unset GMAIL_AUTH_CODE
        
        # Restart without auth code
        echo "🔄 Restarting container without auth code..."
        docker compose down
        docker compose up -d
        
        echo "🎉 Gmail bot is now running with fresh authentication!"
    else
        echo "❌ Authentication failed. Check logs:"
        docker compose logs gmail-bot --tail 20
        rm -f .env.auth
        exit 1
    fi
    
    exit 0
fi

# Method 2: Interactive mode
echo ""
echo "📋 To re-authenticate Gmail in Docker:"
echo ""
echo "1. Get the authorization URL from bot logs:"
echo "   docker compose logs gmail-bot | grep 'Open this URL'"
echo ""
echo "2. Or start the container to see the URL:"
echo "   docker compose up -d"
echo "   docker compose logs -f gmail-bot"
echo ""
echo "3. Open the URL in your browser and get the authorization code"
echo ""
echo "4. Run this script with the code:"
echo "   ./scripts/reauth.sh YOUR_AUTH_CODE_HERE"
echo ""
echo "🔍 Starting container to show auth URL..."

# Start container to show auth URL
docker compose up -d

echo ""
echo "📺 Showing recent logs (press Ctrl+C when you see the auth URL):"
echo "================================================================"

# Show logs and wait for auth URL
timeout 30 docker compose logs -f gmail-bot || true

echo ""
echo "🔗 If you saw the auth URL above, copy it and complete the authentication."
echo "📞 Then run: ./scripts/reauth.sh YOUR_AUTH_CODE"
