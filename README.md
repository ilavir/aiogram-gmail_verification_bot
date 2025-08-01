# Gmail Verification Code Bot

A Telegram bot that monitors your Gmail inbox for verification codes and forwards them to multiple Telegram chats.

## Features

- 📧 Monitors Gmail inbox for verification emails
- 🔍 Automatically extracts verification codes (4-8 digits, alphanumeric)
- 💬 Supports multiple Telegram chat destinations
- ⚡ Real-time notifications using aiogram
- 🔒 Secure OAuth2 authentication with Gmail
- 📊 Status commands and monitoring
- 🎯 Customizable keywords and check intervals
- 🐳 Docker support for easy deployment
- 📝 Comprehensive logging and error handling

## Production Deployment with Docker

### Prerequisites
- Docker with `docker compose` command support
- Git (to clone the repository)

### Quick Start

1. **Clone and Setup**:
   ```bash
   git clone <your-repo-url>
   cd gmail_cards_bot
   cp .env.production .env
   nano .env  # Configure your credentials
   ```

2. **Deploy**:
   ```bash
   ./deploy.sh
   ```

**⚠️ First-time Gmail Authentication:**
Since servers don't have browsers, see [SERVER_SETUP.md](SERVER_SETUP.md) for authentication options.

### Docker Commands

```bash
# Deploy/Update bot
./deploy.sh

# Start bot
./scripts/start.sh
# or: docker compose up -d

# Stop bot
./scripts/stop.sh
# or: docker compose down

# View logs
./scripts/logs.sh
# or: docker compose logs -f gmail-bot

# Restart bot
./scripts/restart.sh
# or: docker compose restart gmail-bot

# Check status
docker compose ps

# Shell access (for debugging)
docker compose exec gmail-bot /bin/bash
```

### Production Features
- **Persistent Storage**: Gmail tokens stored in Docker volume
- **Log Rotation**: Automatic log rotation (10MB max, 3 files)
- **Resource Limits**: Memory and CPU limits for stability
- **Auto Restart**: Container restarts automatically on failure
- **Health Checks**: Built-in container health monitoring

## Local Development

### 1. Install Dependencies

```bash
# Activate virtual environment
source .venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Choose "Desktop application"
   - **Copy the Client ID and Client Secret** (don't download JSON)
5. Add these to your `.env` file (see step 4)

### 3. Telegram Bot Setup

1. Create a bot with [@BotFather](https://t.me/BotFather)
2. Get your bot token
3. Get your chat ID(s):
   - Start chat with [@userinfobot](https://t.me/userinfobot)
   - Send any message to get your chat ID
   - For groups: Add bot to group, send message, use group ID

### 4. Configuration

```bash
# Run setup script
python setup.py

# Edit .env file with your configuration
cp .env.example .env
nano .env
```

Configure these variables in `.env`:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_IDS=chat_id_1,chat_id_2,chat_id_3  # Comma-separated
TELEGRAM_ADMIN_IDS=admin_chat_id_1,admin_chat_id_2  # Comma-separated admin IDs

# Gmail API Configuration (from Google Cloud Console)
GMAIL_CLIENT_ID=your_gmail_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_gmail_client_secret

# Gmail API Files (optional, defaults shown)
GMAIL_TOKEN_FILE=token.json

# Bot Configuration (optional)
CHECK_INTERVAL=30  # seconds between Gmail checks
VERIFICATION_KEYWORDS=verification,code,verify,2FA,two-factor,OTP,one-time
```

## Usage

### Start the Bot

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the bot
python main.py
```

### First Run

On first run, the bot will:
1. Open a browser for Gmail OAuth authentication
2. Save authentication token for future use
3. Send startup message to all configured chats
4. Start monitoring Gmail

### Bot Commands

**Available to all users:**
- `/start` - Welcome message and basic info
- `/help` - Detailed help and configuration info
- `/status` - Current bot status

**Admin-only commands:**
- `/admin` - Admin panel with detailed bot information
- `/chats` - List all configured chat IDs and admin IDs

## How It Works

1. **Gmail Monitoring**: Bot checks Gmail every 30 seconds (configurable)
2. **Keyword Matching**: Searches for emails containing verification keywords
3. **Code Extraction**: Uses regex patterns to find verification codes
4. **Multi-Chat Delivery**: Sends formatted messages to all configured chats
5. **Admin Notifications**: Sends status messages to dedicated admin chats
6. **Duplicate Prevention**: Tracks processed emails to avoid duplicates

## Verification Code Patterns

The bot recognizes these patterns:
- 6-digit codes: `123456`
- 4-digit codes: `1234`
- 8-digit codes: `12345678`
- 6-character alphanumeric: `ABC123`
- 8-character alphanumeric: `ABCD1234`

## Security Features

- OAuth2 authentication with Gmail (no password storage)
- Separate admin and user chat authorization
- Secure token storage
- Rate limiting protection
- Error handling and logging

## File Structure

```
gmail_cards_bot/
├── scripts/              # Docker management scripts
│   ├── start.sh         # Start containers
│   ├── stop.sh          # Stop containers
│   ├── restart.sh       # Restart containers
│   └── logs.sh          # View logs
├── logs/                # Application logs
│   └── bot.log          # Main log file
├── .venv/               # Virtual environment
├── main.py              # Main application
├── config.py            # Configuration management
├── gmail_service.py     # Gmail API integration
├── telegram_service.py  # Telegram bot service
├── auth_gmail.py        # Gmail authentication helper
├── setup.py             # Setup script
├── deploy.sh            # Docker deployment script
├── compose.yml          # Docker Compose configuration
├── Dockerfile           # Docker image definition
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── .env.production      # Production environment template
├── .env                 # Your configuration (create this)
├── token.json           # Gmail auth token (auto-generated)
├── SERVER_SETUP.md      # Server authentication guide
├── DEPLOYMENT.md        # Deployment instructions
└── README.md            # This file
```

## Troubleshooting

### Gmail Authentication Issues
- Ensure `GMAIL_CLIENT_ID` and `GMAIL_CLIENT_SECRET` are set in `.env`
- Check that Gmail API is enabled in Google Cloud Console
- Verify OAuth consent screen is configured

### Telegram Issues
- Verify bot token is correct
- Ensure chat IDs are correct (including negative signs for groups)
- Check that bot has permission to send messages

### Common Errors
- `TELEGRAM_BOT_TOKEN is required`: Set token in `.env` file
- `TELEGRAM_CHAT_IDS is required`: Set chat IDs in `.env` file
- `GMAIL_CLIENT_ID is required`: Set Gmail client ID in `.env` file
- `GMAIL_CLIENT_SECRET is required`: Set Gmail client secret in `.env` file

## Logs

Check logs for detailed operation logs:
```bash
# View current logs
tail -f logs/bot.log

# For Docker deployment
docker compose logs -f gmail-bot
```

## Customization

### Adding Keywords
Edit `VERIFICATION_KEYWORDS` in `.env`:
```env
VERIFICATION_KEYWORDS=verification,code,verify,2FA,OTP,login,security,auth
```

### Changing Check Interval
Edit `CHECK_INTERVAL` in `.env` (in seconds):
```env
CHECK_INTERVAL=60  # Check every minute
```

### Multiple Chat Support
Add multiple chat IDs separated by commas:
```env
TELEGRAM_CHAT_IDS=123456789,-987654321,555666777
TELEGRAM_ADMIN_IDS=123456789,987654321  # Admin IDs for status messages
```

## License

This project is open source. Use responsibly and in accordance with Gmail and Telegram Terms of Service.
