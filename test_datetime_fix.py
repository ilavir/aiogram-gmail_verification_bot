#!/usr/bin/env python3
"""
Test datetime fix for Gmail service
"""

import asyncio
from datetime import datetime, timezone
from gmail_service import GmailService
from config import config


async def test_datetime_handling():
    """Test that datetime handling works correctly"""
    print("🧪 Testing datetime handling fix...")

    try:
        # Create Gmail service
        service = GmailService(
            client_id=config.gmail_client_id,
            client_secret=config.gmail_client_secret,
            token_file=config.gmail_token_file,
            scopes=config.gmail_scopes
        )

        print("✅ GmailService created successfully")
        print(f"✅ last_check_time: {service.last_check_time}")
        print(f"✅ Timezone aware: {service.last_check_time.tzinfo is not None}")

        # Test date parsing with various formats
        test_dates = [
            "Mon, 7 Jul 2025 12:00:00 +0000",
            "Tue, 8 Jul 2025 15:30:45 -0500",
            "Wed, 9 Jul 2025 09:15:30 +0200"
        ]

        for date_str in test_dates:
            parsed_date = service._parse_date(date_str)
            print(f"✅ Parsed '{date_str}' -> {parsed_date}")
            print(f"   Timezone aware: {parsed_date.tzinfo is not None}")

            # Test comparison (should not raise datetime comparison error)
            is_new = service._is_new_message(parsed_date)
            print(f"   Comparison works: {is_new}")

        print("\n🎉 All datetime operations successful!")
        print("✅ The 'can't compare offset-naive and offset-aware datetimes' error is fixed!")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_datetime_handling())
