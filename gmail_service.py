import os
import pickle
import base64
import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)


class GmailService:
    def __init__(self, client_id: str, client_secret: str, token_file: str,
                 scopes: List[str], telegram_service=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_file = token_file
        self.scopes = scopes
        self.service = None
        self.telegram_service = telegram_service
        # Start 5 minutes ago with timezone awareness
        self.last_check_time = datetime.now(timezone.utc) - timedelta(minutes=5)

    async def send_auth_error_notification(self):
        """Send Telegram notification when Gmail authentication is required"""
        if self.telegram_service:
            try:
                message = (
                    "🚨 *Gmail Authentication Required*\n\n"
                    "The Gmail bot token has expired and needs manual re-authentication.\n\n"
                    "*To fix this (Docker):*\n"
                    "1. `./scripts/stop.sh`\n"
                    "2. `docker volume rm gmail_cards_bot_gmail_data`\n"
                    "3. Re-authenticate locally:\n"
                    "   • `source .venv/bin/activate`\n"
                    "   • `python auth_gmail.py`\n"
                    "4. `./scripts/start.sh`\n\n"
                    "The bot will stop checking Gmail until this is resolved."
                )
                await self.telegram_service.send_status_message(message)
                logger.info("Sent Gmail authentication error notification to admin")
            except Exception as e:
                logger.error(f"Failed to send auth error notification: {e}")

    async def authenticate(self) -> bool:
        """Authenticate with Gmail API using environment variables"""
        try:
            creds = None
            # Load existing token
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)

            # If there are no (valid) credentials available, let user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        # Attempt to refresh the token
                        creds.refresh(Request())
                        logger.info("Token refreshed successfully")
                    except Exception as refresh_error:
                        logger.warning(f"Token refresh failed: {refresh_error}")
                        # If refresh fails, clear credentials and re-authenticate
                        creds = None

                # If we still don't have valid credentials, re-authenticate
                if not creds or not creds.valid:
                    logger.info("Re-authenticating due to invalid/expired credentials")

                    # Create credentials config from environment variables
                    client_config = {
                        "installed": {
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"]
                        }
                    }

                    flow = InstalledAppFlow.from_client_config(
                        client_config, self.scopes
                    )
                    # Use headless authentication for server environments
                    creds = await self._headless_auth(flow)

            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)

            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail authentication successful")
            return True

        except Exception as e:
            logger.error(f"Gmail authentication failed: {e}")
            # Clean up corrupted token file
            if os.path.exists(self.token_file):
                try:
                    os.remove(self.token_file)
                    logger.info("Removed corrupted token file")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to remove token file: {cleanup_error}")
            return False

    async def _headless_auth(self, flow):
        """Perform headless OAuth authentication"""
        # Configure the flow for out-of-band (manual) authentication
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'

        # Get the authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent'
        )

        logger.info("=" * 60)
        logger.info("🔐 GMAIL AUTHENTICATION REQUIRED")
        logger.info("=" * 60)
        logger.info("Please complete the following steps:")
        logger.info("1. Open this URL in your browser:")
        logger.info("   %s", auth_url)
        logger.info("2. Complete the authorization process")
        logger.info("3. Copy the authorization code from the browser")
        logger.info("4. Enter the code when prompted")
        logger.info("=" * 60)

        # In a container environment, we need to handle this differently
        if os.path.exists('/.dockerenv'):
            logger.info("🐳 DOCKER CONTAINER DETECTED")
            logger.info("Since you're running in Docker, you have two options:")
            logger.info("")
            logger.info("OPTION 1 - Manual Setup (Recommended):")
            logger.info("1. Stop the container: docker compose down")
            logger.info("2. Run locally first: python main.py")
            logger.info("3. Complete OAuth authentication")
            logger.info("4. Copy token.json to your server")
            logger.info("5. Restart container: docker compose up -d")
            logger.info("")
            logger.info("OPTION 2 - Container Setup:")
            logger.info("1. Open the URL above in your browser")
            logger.info("2. Get the authorization code")
            logger.info("3. Set environment variable: "
                        "GMAIL_AUTH_CODE=your_code")
            logger.info("4. Restart the container")
            logger.info("")

            # Check if auth code is provided via environment variable
            auth_code = os.getenv('GMAIL_AUTH_CODE')
            if auth_code:
                logger.info("Using provided authorization code...")
                flow.fetch_token(code=auth_code.strip())
                return flow.credentials
            else:
                logger.error(
                    "No authorization code provided. Please use OPTION 1 "
                    "or set GMAIL_AUTH_CODE environment variable."
                )
                raise Exception(
                    "Gmail authentication required - see logs for instructions"
                )
        else:
            # Interactive mode for local development
            print("\n" + "=" * 60)
            print("🔐 GMAIL AUTHENTICATION REQUIRED")
            print("=" * 60)
            print("1. Open this URL in your browser:")
            print(f"   {auth_url}")
            print("2. Complete the authorization process")
            print("3. Copy the authorization code and paste it below")
            print("=" * 60)

            auth_code = input("Enter authorization code: ").strip()
            flow.fetch_token(code=auth_code)
            return flow.credentials

    async def get_recent_messages(self, keywords: List[str]) -> List[Dict]:
        """Get recent messages containing verification keywords"""
        if not self.service:
            logger.error("Gmail service not authenticated")
            return []

        try:
            # Create query for verification emails
            keyword_query = ' OR '.join([
                f'subject:{keyword}' for keyword in keywords
            ])
            query = f'({keyword_query}) AND newer_than:1h'

            # Get message list
            result = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()

            messages = result.get('messages', [])
            verification_messages = []

            for message in messages:
                msg_data = await self._get_message_details(message['id'])
                if msg_data and self._is_new_message(msg_data['date']):
                    verification_messages.append(msg_data)

            # Update last check time
            self.last_check_time = datetime.now(timezone.utc)
            return verification_messages

        except HttpError as error:
            logger.error(f'Gmail API error: {error}')
            return []
        except Exception as e:
            error_str = str(e)
            logger.error(f'Error getting messages: {e}')

            # Check if this is an auth error that requires manual intervention
            if 'invalid_grant' in error_str or 'Token has been expired or revoked' in error_str:
                logger.critical("Gmail authentication expired - manual re-authentication required!")
                await self.send_auth_error_notification()

            return []

    async def _get_message_details(self, message_id: str) -> Optional[Dict]:
        """Get detailed information about a message"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            headers = message['payload'].get('headers', [])
            subject = next((
                h['value'] for h in headers if h['name'] == 'Subject'
            ), 'No Subject')
            sender = next((
                h['value'] for h in headers if h['name'] == 'From'
            ), 'Unknown Sender')
            date_str = next((
                h['value'] for h in headers if h['name'] == 'Date'
            ), '')

            # Extract message body
            body = self._extract_message_body(message['payload'])

            # Extract verification codes
            codes = self._extract_verification_codes(subject + ' ' + body)

            return {
                'id': message_id,
                'subject': subject,
                'sender': sender,
                'date': self._parse_date(date_str),
                'body': body[:500],  # Limit body length
                'codes': codes
            }

        except Exception as e:
            logger.error(f'Error getting message details: {e}')
            return None

    def _extract_message_body(self, payload) -> str:
        """Extract text from message payload (both plain text and HTML)"""
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    data = part['body']['data']
                    body += base64.urlsafe_b64decode(data).decode('utf-8')
                elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                    data = part['body']['data']
                    html_content = base64.urlsafe_b64decode(data).decode('utf-8')
                    # Extract text from HTML using simple regex
                    import re
                    # Remove HTML tags and get text content
                    text_content = re.sub(r'<[^>]+>', ' ', html_content)
                    # Clean up whitespace
                    text_content = re.sub(r'\s+', ' ', text_content).strip()
                    body += text_content
        elif payload['mimeType'] == 'text/plain' and 'data' in payload['body']:
            data = payload['body']['data']
            body = base64.urlsafe_b64decode(data).decode('utf-8')
        elif payload['mimeType'] == 'text/html' and 'data' in payload['body']:
            data = payload['body']['data']
            html_content = base64.urlsafe_b64decode(data).decode('utf-8')
            # Extract text from HTML using simple regex
            import re
            # Remove HTML tags and get text content
            text_content = re.sub(r'<[^>]+>', ' ', html_content)
            # Clean up whitespace
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            body = text_content

        return body

    def _extract_verification_codes(self, text: str) -> List[str]:
        """Extract verification codes from text using regex patterns"""
        patterns = [
            r'\b\d{6}\b',  # 6-digit codes
            # r'\b\d{4}\b',  # 4-digit codes
            # r'\b\d{8}\b',  # 8-digit codes
            # r'\b[A-Z0-9]{6}\b',  # 6-character alphanumeric codes
            # r'\b[A-Z0-9]{8}\b',  # 8-character alphanumeric codes
        ]

        codes = []
        for pattern in patterns:
            matches = re.findall(pattern, text.upper())
            codes.extend(matches)

        # Remove duplicates and filter out common false positives
        codes = list(set(codes))
        codes = [code for code in codes if not self._is_false_positive(code)]

        return codes

    def _is_false_positive(self, code: str) -> bool:
        """Check if code is likely a false positive"""
        false_positives = ['2024', '2025', '1234', '0000', '9999', '000000']
        return code in false_positives

    def _parse_date(self, date_str: str) -> datetime:
        """Parse email date string to datetime with timezone awareness"""
        try:
            # Gmail date format: "Mon, 1 Jan 2024 12:00:00 +0000"
            from email.utils import parsedate_to_datetime
            parsed_date = parsedate_to_datetime(date_str)

            # If the parsed date is timezone-naive, assume UTC
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)

            return parsed_date
        except Exception as e:
            logger.warning(f"Failed to parse date '{date_str}': {e}")
            # Return current time in UTC as fallback
            return datetime.now(timezone.utc)

    def _is_new_message(self, message_date: datetime) -> bool:
        """Check if message is newer than last check"""
        # Ensure both datetimes are timezone-aware for comparison
        if message_date.tzinfo is None:
            message_date = message_date.replace(tzinfo=timezone.utc)

        if self.last_check_time.tzinfo is None:
            self.last_check_time = self.last_check_time.replace(tzinfo=timezone.utc)

        return message_date > self.last_check_time
