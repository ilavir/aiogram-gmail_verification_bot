#!/usr/bin/env python3
"""
Setup script for Gmail Verification Bot
"""

import sys
from pathlib import Path


def create_env_file():
    """Create .env file from template"""
    env_example = Path('.env.example')
    env_file = Path('.env')

    if env_file.exists():
        print("✅ .env file already exists")
        return

    if not env_example.exists():
        print("❌ .env.example file not found")
        return

    # Copy template
    with open(env_example, 'r') as f:
        content = f.read()

    with open(env_file, 'w') as f:
        f.write(content)

    print("✅ Created .env file from template")
    print("📝 Please edit .env file with your configuration")


def check_credentials():
    """Check Gmail credentials configuration"""
    print("\n📧 Gmail API Setup:")
    print("   Using environment variables for secure credential management")
    print("   This is more secure for GitHub repositories!")
    print()
    print("   1. Go to https://console.cloud.google.com/")
    print("   2. Create a new project or select existing")
    print("   3. Enable Gmail API")
    print("   4. Create OAuth 2.0 credentials (Desktop application)")
    print("   5. Copy the Client ID and Client Secret")
    print("   6. Add them to your .env file:")
    print("      GMAIL_CLIENT_ID=your_client_id.apps.googleusercontent.com")
    print("      GMAIL_CLIENT_SECRET=your_client_secret")


def get_chat_id_instructions():
    """Show instructions for getting Telegram chat ID"""
    print("\n📱 To get your Telegram Chat ID:")
    print("   1. Start a chat with @userinfobot")
    print("   2. Send any message")
    print("   3. Copy the 'Id' number (including negative sign if present)")
    print("   4. For groups: Add bot to group, send a message, use group ID")
    print("   5. Multiple IDs: separate with commas (e.g., 123456,-789012)")


def main():
    """Main setup function"""
    print("🤖 Gmail Verification Bot Setup")
    print("=" * 40)

    # Check if we're in virtual environment
    if not hasattr(sys, 'real_prefix') and not (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    ):
        print("⚠️  Warning: Not in virtual environment")
        print("   Consider running: source .venv/bin/activate")

    # Create .env file
    create_env_file()

    # Check credentials
    check_credentials()

    # Show chat ID instructions
    get_chat_id_instructions()

    print("\n🚀 Next steps:")
    print("   1. Edit .env file with your tokens, chat IDs, and Gmail "
          "credentials")
    print("   2. Run: python main.py")
    print("   3. Complete Gmail OAuth in browser on first run")

    print("\n🔒 Security Note:")
    print("   • Never commit .env file to Git")
    print("   • Use environment variables in production")
    print("   • The .env file is already in .gitignore")

    print("\n📚 For detailed setup instructions, see README.md")


if __name__ == "__main__":
    main()
