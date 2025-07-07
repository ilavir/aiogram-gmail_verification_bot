#!/usr/bin/env python3
"""
Test OAuth Configuration
Quick test to verify Gmail OAuth setup
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_oauth():
    """Test OAuth configuration"""
    print("🔧 Testing OAuth Configuration...")

    client_id = os.getenv('GMAIL_CLIENT_ID')
    client_secret = os.getenv('GMAIL_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("❌ Missing GMAIL_CLIENT_ID or GMAIL_CLIENT_SECRET in .env file")
        return False

    print(f"✅ Client ID: {client_id[:20]}...")
    print(f"✅ Client Secret: {'*' * len(client_secret)}")

    # Create client config
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"]
        }
    }

    try:
        # Create flow
        flow = InstalledAppFlow.from_client_config(
            client_config,
            ['https://www.googleapis.com/auth/gmail.readonly']
        )

        # Set redirect URI explicitly
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'

        # Generate auth URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent'
        )

        print("✅ OAuth flow created successfully!")
        print("\n🔗 Authorization URL:")
        print(auth_url)
        print("\n📋 Instructions:")
        print("1. Open the URL above in your browser")
        print("2. Complete the authorization")
        print("3. Copy the authorization code")
        print("4. Paste it below")

        auth_code = input("\nEnter authorization code: ").strip()

        if auth_code:
            flow.fetch_token(code=auth_code)
            print("✅ Token obtained successfully!")
            print("🎉 OAuth configuration is working!")
            return True
        else:
            print("❌ No authorization code provided")
            return False

    except Exception as e:
        print(f"❌ OAuth test failed: {e}")
        return False

if __name__ == "__main__":
    test_oauth()
