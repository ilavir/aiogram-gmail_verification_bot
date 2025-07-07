#!/bin/bash
# Restart Gmail Verification Bot
echo "🔄 Restarting Gmail Verification Bot..."
docker compose restart gmail-bot
docker compose ps
echo "✅ Bot restarted successfully"
