# Server Deployment Guide

## Gmail Authentication for Headless Servers

Since your Ubuntu server doesn't have a browser, you have **3 options** for Gmail authentication:

## Option 1: Local Authentication (Recommended) 🏆

**Best for: Most users**

1. **Setup locally first:**
   ```bash
   # On your local machine
   git clone <your-repo>
   cd gmail_cards_bot
   cp .env.production .env
   nano .env  # Add your credentials
   
   # Install dependencies
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   
   # Authenticate with Gmail
   python auth_gmail.py
   ```

2. **Copy token to server:**
   ```bash
   # Copy token.json to your server
   scp token.json user@your-server:/path/to/gmail_cards_bot/
   ```

3. **Deploy on server:**
   ```bash
   # On your server
   ./deploy.sh
   ```

## Option 2: Manual Authorization Code 🔧

**Best for: Advanced users who want to do everything on the server**

1. **Start the bot on server:**
   ```bash
   ./deploy.sh
   ```

2. **Check logs for auth URL:**
   ```bash
   docker compose logs gmail-bot
   ```

3. **Complete authentication:**
   - Copy the authorization URL from logs
   - Open it in your browser (on any device)
   - Complete the OAuth process
   - Copy the authorization code

4. **Provide the code:**
   ```bash
   # Stop the container
   docker compose down
   
   # Add auth code to .env file
   echo "GMAIL_AUTH_CODE=your_authorization_code_here" >> .env
   
   # Restart
   docker compose up -d
   
   # Remove auth code from .env (security)
   sed -i '/GMAIL_AUTH_CODE/d' .env
   ```

## Option 3: Pre-generated Token 📁

**Best for: CI/CD or automated deployments**

1. **Generate token elsewhere:**
   - Use Option 1 on any machine with a browser
   - Or use Google Cloud Shell

2. **Upload token directly:**
   ```bash
   # Create the data directory
   mkdir -p data
   
   # Copy your token.json to data/token.json
   cp token.json data/
   
   # Deploy
   ./deploy.sh
   ```

## Troubleshooting

### "No authorization code provided" Error
```bash
# Check logs
docker compose logs gmail-bot

# The logs will show you the authorization URL
# Follow Option 2 above
```

### Token Expired
```bash
# Remove old token
docker compose down
docker volume rm gmail_cards_bot_gmail_data

# Re-authenticate using any option above
```

### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x *.sh scripts/*.sh
```

## Security Notes

- ✅ **Never commit `token.json`** - it's in `.gitignore`
- ✅ **Remove `GMAIL_AUTH_CODE`** from `.env` after use
- ✅ **Use Option 1** for the most secure setup
- ✅ **Tokens auto-refresh** once initially created

## Quick Commands

```bash
# Check if authentication is working
docker compose logs gmail-bot | grep -i auth

# View real-time logs
docker compose logs -f gmail-bot

# Restart if needed
docker compose restart gmail-bot

# Check container status
docker compose ps
```
