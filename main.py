import asyncio
import logging
import os
from datetime import datetime, timezone
from config import config
from gmail_service import GmailService
from telegram_service import TelegramService

# Setup logging
log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
log_handlers = [logging.StreamHandler()]

# Add file handler if logs directory exists
if os.path.exists('/app/logs'):
    log_handlers.append(logging.FileHandler('/app/logs/bot.log'))
elif os.path.exists('logs'):
    log_handlers.append(logging.FileHandler('logs/bot.log'))
else:
    log_handlers.append(logging.FileHandler('bot.log'))

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=log_handlers
)

logger = logging.getLogger(__name__)


class GmailVerificationBot:
    def __init__(self):
        self.config = config
        self.gmail_service = GmailService(
            client_id=self.config.gmail_client_id,
            client_secret=self.config.gmail_client_secret,
            token_file=self.config.gmail_token_file,
            scopes=self.config.gmail_scopes
        )
        self.telegram_service = TelegramService(self.config)
        self.running = False

    async def initialize(self):
        """Initialize services"""
        logger.info("Initializing Gmail Verification Bot...")

        # Authenticate Gmail
        if not await self.gmail_service.authenticate():
            raise Exception("Failed to authenticate with Gmail")

        logger.info("Gmail authentication successful")

        # Send startup message to first chat only
        startup_message = (
            f"🤖 <b>Gmail Verification Bot Started</b>\n\n"
            f"🕐 <b>Started at:</b> "
            f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"⏱️ <b>Check interval:</b> {self.config.check_interval} seconds\n"
            f"🔍 <b>Monitoring keywords:</b> "
            f"{', '.join(self.config.verification_keywords)}\n"
            f"💬 <b>Target chats:</b> {len(self.config.telegram_chat_ids)}\n\n"
            f"✅ Ready to monitor Gmail for verification codes!"
        )

        await self.telegram_service.send_status_message(startup_message)
        logger.info("Bot initialized successfully")

    async def check_gmail(self):
        """Check Gmail for new verification messages"""
        try:
            messages = await self.gmail_service.get_recent_messages(
                self.config.verification_keywords
            )

            if messages:
                logger.info(f"Found {len(messages)} verification messages")
                await self.telegram_service.send_verification_message(messages)

        except Exception as e:
            logger.error(f"Error checking Gmail: {e}")

    async def monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Starting Gmail monitoring loop...")
        self.running = True

        while self.running:
            try:
                await self.check_gmail()
                await asyncio.sleep(self.config.check_interval)
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, stopping...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.config.check_interval)

    async def run_bot_polling(self):
        """Run Telegram bot polling in background"""
        try:
            await self.telegram_service.start_polling()
        except Exception as e:
            logger.error(f"Error in bot polling: {e}")

    async def run(self):
        """Run the bot"""
        try:
            await self.initialize()

            # Create tasks for monitoring and bot polling
            monitoring_task = asyncio.create_task(self.monitoring_loop())
            polling_task = asyncio.create_task(self.run_bot_polling())

            # Wait for either task to complete (or fail)
            done, pending = await asyncio.wait(
                [monitoring_task, polling_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel remaining tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up...")

        # Send shutdown message
        shutdown_message = (
            f"🔴 <b>Gmail Verification Bot Stopped</b>\n\n"
            f"🕐 <b>Stopped at:</b> "
            f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"👋 Bot is no longer monitoring Gmail."
        )

        try:
            await self.telegram_service.send_status_message(shutdown_message)
        except Exception:
            pass

        await self.telegram_service.close()
        logger.info("Cleanup completed")


async def main():
    """Main entry point"""
    bot = GmailVerificationBot()
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
