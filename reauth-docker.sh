#!/bin/bash
# Quick Docker Gmail Re-auth
# Usage: ./reauth-docker.sh AUTH_CODE

if [ -z "$1" ]; then
    echo "Usage: ./reauth-docker.sh YOUR_AUTH_CODE"
    echo "First run 'docker compose logs gmail-bot' to get the auth URL"
    exit 1
fi

echo "🔄 Re-authenticating Gmail in Docker..."
docker compose down
GMAIL_AUTH_CODE="$1" docker compose up -d
sleep 10
docker compose restart gmail-bot
echo "✅ Done! Check: docker compose logs -f gmail-bot"
