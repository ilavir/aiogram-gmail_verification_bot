from dataclasses import dataclass
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Config:
    # Telegram Configuration
    telegram_bot_token: str
    telegram_chat_ids: List[str]
    telegram_admin_ids: List[str]

    # Gmail Configuration
    gmail_client_id: str
    gmail_client_secret: str
    gmail_token_file: str
    gmail_scopes: List[str]

    # Bot Configuration
    check_interval: int
    verification_keywords: List[str]

    @classmethod
    def from_env(cls) -> 'Config':
        """Create Config instance from environment variables"""
        telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        telegram_chat_ids_str = os.getenv('TELEGRAM_CHAT_IDS')
        telegram_admin_ids_str = os.getenv('TELEGRAM_ADMIN_IDS')
        gmail_client_id = os.getenv('GMAIL_CLIENT_ID')
        gmail_client_secret = os.getenv('GMAIL_CLIENT_SECRET')

        if not telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not telegram_chat_ids_str:
            raise ValueError("TELEGRAM_CHAT_IDS is required")
        if not telegram_admin_ids_str:
            raise ValueError("TELEGRAM_ADMIN_IDS is required")
        if not gmail_client_id:
            raise ValueError("GMAIL_CLIENT_ID is required")
        if not gmail_client_secret:
            raise ValueError("GMAIL_CLIENT_SECRET is required")

        # Parse chat IDs (comma-separated)
        telegram_chat_ids = [
            chat_id.strip() for chat_id in telegram_chat_ids_str.split(',')
        ]

        # Parse admin IDs (comma-separated)
        telegram_admin_ids = [
            admin_id.strip() for admin_id in telegram_admin_ids_str.split(',')
        ]

        return cls(
            telegram_bot_token=telegram_bot_token,
            telegram_chat_ids=telegram_chat_ids,
            telegram_admin_ids=telegram_admin_ids,
            gmail_client_id=gmail_client_id,
            gmail_client_secret=gmail_client_secret,
            gmail_token_file=os.getenv('GMAIL_TOKEN_FILE', 'token.json'),
            gmail_scopes=['https://www.googleapis.com/auth/gmail.readonly'],
            check_interval=int(os.getenv('CHECK_INTERVAL', 30)),
            verification_keywords=os.getenv(
                'VERIFICATION_KEYWORDS',
                'verification,code,verify,2FA,two-factor,OTP,one-time'
            ).split(',')
        )


# Global config instance
config = Config.from_env()
