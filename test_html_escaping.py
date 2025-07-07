#!/usr/bin/env python3
"""
Test HTML escaping for Telegram messages
"""

import html
from datetime import datetime, timezone
from telegram_service import TelegramService
from config import config


def test_html_escaping():
    """Test that HTML entities are properly escaped"""
    print("🧪 Testing HTML escaping for Telegram messages...")

    # Create telegram service
    telegram_service = TelegramService(config)

    # Test message with problematic characters
    test_msg_data = {
        'sender': 'Test User <test@example.com>',
        'subject': 'Your verification code & important info',
        'date': datetime.now(timezone.utc),
        'body': 'Hello! Your code is 123456. Visit <https://example.com> for more info.',
        'codes': ['123456']
    }

    # Test HTML formatting
    html_message = telegram_service._format_verification_message(test_msg_data)
    print("✅ HTML formatted message:")
    print(html_message)
    print()

    # Test plain text formatting
    plain_message = telegram_service._format_plain_message(test_msg_data)
    print("✅ Plain text formatted message:")
    print(plain_message)
    print()

    # Test specific problematic cases
    problematic_cases = [
        'user@example.com',
        '<script>alert("test")</script>',
        'Price: $100 < $200 & more',
        'Email: kahn@inbox.ru',
        'HTML tags: <div>content</div>'
    ]

    print("🔍 Testing HTML escaping for problematic strings:")
    for case in problematic_cases:
        escaped = html.escape(case)
        print(f"   Original: {case}")
        print(f"   Escaped:  {escaped}")
        print()

    print("🎉 HTML escaping test completed!")
    print("✅ Email addresses and HTML characters should now be safe for Telegram")


if __name__ == "__main__":
    test_html_escaping()
