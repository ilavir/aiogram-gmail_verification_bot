# Deployment Guide

## Security Best Practices

### 🔒 Environment Variables
Never commit sensitive data to Git. Use environment variables instead:

```bash
# Set environment variables (Linux/macOS)
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_IDS="123456,-789012"
export GMAIL_CLIENT_ID="your_client_id.apps.googleusercontent.com"
export GMAIL_CLIENT_SECRET="your_client_secret"
```

### 🐳 Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  gmail-bot:
    build: .
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHAT_IDS=${TELEGRAM_CHAT_IDS}
      - GMAIL_CLIENT_ID=${GMAIL_CLIENT_ID}
      - GMAIL_CLIENT_SECRET=${GMAIL_CLIENT_SECRET}
    volumes:
      - ./token.json:/app/token.json
    restart: unless-stopped
```

### ☁️ Cloud Deployment

#### Heroku
```bash
# Set config vars
heroku config:set TELEGRAM_BOT_TOKEN="your_token"
heroku config:set TELEGRAM_CHAT_IDS="123456,-789012"
heroku config:set GMAIL_CLIENT_ID="your_client_id"
heroku config:set GMAIL_CLIENT_SECRET="your_secret"
```

#### AWS/GCP/Azure
Use their respective secret management services:
- AWS: Systems Manager Parameter Store / Secrets Manager
- GCP: Secret Manager
- Azure: Key Vault

### 🔐 GitHub Secrets
For GitHub Actions, use repository secrets:
1. Go to Settings → Secrets and variables → Actions
2. Add secrets:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_IDS`
   - `GMAIL_CLIENT_ID`
   - `GMAIL_CLIENT_SECRET`

### 📋 Production Checklist

- [ ] Environment variables configured
- [ ] `.env` file in `.gitignore`
- [ ] No sensitive data in code
- [ ] OAuth consent screen configured
- [ ] Bot permissions verified
- [ ] Logging configured
- [ ] Error monitoring setup
- [ ] Backup strategy for `token.json`

### 🚨 What NOT to commit:
- `.env` files
- `token.json`
- Any files containing secrets
- API keys or tokens

### ✅ Safe to commit:
- Source code
- `requirements.txt`
- `.env.example`
- Documentation
- Configuration templates
