#!/usr/bin/env python3
"""
Gmail Authentication Helper Script
Run this locally to generate token.json, then copy it to your server.
"""

import asyncio
import sys
from config import config
from gmail_service import GmailService


async def main():
    """Authenticate with Gmail and save token"""
    print("🔐 Gmail Authentication Helper")
    print("=" * 40)

    try:
        # Create Gmail service
        gmail_service = GmailService(
            client_id=config.gmail_client_id,
            client_secret=config.gmail_client_secret,
            token_file=config.gmail_token_file,
            scopes=config.gmail_scopes
        )

        # Authenticate
        if await gmail_service.authenticate():
            print("✅ Authentication successful!")
            print(f"📁 Token saved to: {config.gmail_token_file}")
            print("")
            print("🚀 Next steps for server deployment:")
            print(f"1. Copy {config.gmail_token_file} to your server")
            print("2. Place it in the same directory as your bot")
            print("3. Start your bot - it will use the existing token")
            print("")
            print("📋 For Docker deployment:")
            print("   The token will be automatically mounted to the container")
        else:
            print("❌ Authentication failed!")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
