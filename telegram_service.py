import asyncio
import logging
import html
from datetime import timezone
from typing import List, Dict
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from config import Config

logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self, config: Config):
        self.config = config
        self.bot = Bot(token=config.telegram_bot_token)
        self.dp = Dispatcher()
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup message handlers"""
        self.dp.message.register(self.start_command, Command("start"))
        self.dp.message.register(self.help_command, Command("help"))
        self.dp.message.register(self.status_command, Command("status"))
        self.dp.message.register(self.chats_command, Command("chats"))
        self.dp.message.register(self.admin_command, Command("admin"))

    async def start_command(self, message: Message):
        """Handle /start command"""
        welcome_text = (
            "🤖 Gmail Verification Code Bot\n\n"
            "I'll monitor your Gmail inbox and forward verification codes "
            "to configured chats.\n\n"
            "Commands:\n"
            "/start - Show this message\n"
            "/help - Show help information\n"
            "/status - Check bot status\n"
            "/chats - List configured chat IDs (admin only)\n"
            "/admin - Admin panel (admin only)"
        )
        await message.answer(welcome_text)

    async def help_command(self, message: Message):
        """Handle /help command"""
        help_text = (
            "📧 Gmail Verification Code Bot Help\n\n"
            "This bot monitors your Gmail inbox for verification codes and "
            "forwards them to configured chats.\n\n"
            "🔍 What I look for:\n"
            "• Emails with keywords: verification, code, verify, 2FA, OTP\n"
            "• 4-8 digit verification codes\n"
            "• Alphanumeric verification codes\n\n"
            "⚙️ Configuration:\n"
            f"• Check interval: {self.config.check_interval} seconds\n"
            f"• Keywords: {', '.join(self.config.verification_keywords)}\n"
            f"• Target chats: {len(self.config.telegram_chat_ids)} "
            f"configured\n"
            f"• Admin chats: {len(self.config.telegram_admin_ids)} "
            f"configured\n\n"
            "Commands:\n"
            "/start - Welcome message\n"
            "/help - This help message\n"
            "/status - Bot status\n"
            "/chats - List configured chat IDs (admin only)\n"
            "/admin - Admin panel (admin only)"
        )
        await message.answer(help_text)

    async def status_command(self, message: Message):
        """Handle /status command"""
        status_text = (
            "🟢 Bot Status: Active\n\n"
            f"📧 Gmail monitoring: Enabled\n"
            f"⏱️ Check interval: {self.config.check_interval}s\n"
            f"💬 Target chats: {len(self.config.telegram_chat_ids)}\n"
            f"🔍 Keywords: {len(self.config.verification_keywords)} configured"
        )
        await message.answer(status_text)

    async def chats_command(self, message: Message):
        """Handle /chats command - show configured chat IDs (admin only)"""
        if not self.is_admin(str(message.chat.id)):
            await message.answer(
                "❌ You're not authorized to view this information. "
                "This command is only available to administrators."
            )
            return

        chats_text = "💬 Configured Chat IDs:\n\n"
        for i, chat_id in enumerate(self.config.telegram_chat_ids, 1):
            # Try to get chat info
            try:
                chat = await self.bot.get_chat(chat_id)
                chat_name = (
                    chat.title or chat.first_name or
                    chat.username or "Unknown"
                )
                chats_text += f"{i}. {chat_name} ({chat_id})\n"
            except Exception:
                chats_text += f"{i}. Chat ID: {chat_id} (Info unavailable)\n"

        chats_text += f"\n👑 Admin IDs:\n"
        for i, admin_id in enumerate(self.config.telegram_admin_ids, 1):
            try:
                chat = await self.bot.get_chat(admin_id)
                admin_name = (
                    chat.title or chat.first_name or
                    chat.username or "Unknown"
                )
                chats_text += f"{i}. {admin_name} ({admin_id})\n"
            except Exception:
                chats_text += f"{i}. Admin ID: {admin_id} (Info unavailable)\n"

        await message.answer(chats_text)

    async def admin_command(self, message: Message):
        """Handle /admin command - show admin information (admin only)"""
        if not self.is_admin(str(message.chat.id)):
            await message.answer(
                "❌ You're not authorized to use this command. "
                "This command is only available to administrators."
            )
            return

        admin_text = (
            "👑 <b>Admin Panel</b>\n\n"
            f"🤖 <b>Bot Status:</b> Active\n"
            f"📧 <b>Gmail monitoring:</b> Enabled\n"
            f"⏱️ <b>Check interval:</b> {self.config.check_interval}s\n"
            f"💬 <b>Target chats:</b> {len(self.config.telegram_chat_ids)}\n"
            f"👑 <b>Admin chats:</b> {len(self.config.telegram_admin_ids)}\n"
            f"🔍 <b>Keywords:</b> {len(self.config.verification_keywords)} configured\n\n"
            f"<b>Admin Commands:</b>\n"
            f"/admin - This admin panel\n"
            f"/chats - View all configured chats\n"
            f"/status - Bot status (available to all)\n\n"
            f"<b>Your Chat ID:</b> <code>{message.chat.id}</code>"
        )

        await message.answer(admin_text, parse_mode='HTML')

    async def send_verification_message(self, messages: List[Dict]):
        """Send verification code messages to all target chats"""
        for msg_data in messages:
            # Format the message
            text = self._format_verification_message(msg_data)

            # Send to all configured chats
            for chat_id in self.config.telegram_chat_ids:
                try:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        parse_mode='HTML'
                    )
                    logger.info(
                        f"Sent verification message to chat {chat_id} "
                        f"from {msg_data['sender']}"
                    )

                except Exception as e:
                    logger.error(
                        f"Error sending message to chat {chat_id}: {e}"
                    )
                    # Try sending without HTML formatting as fallback
                    try:
                        plain_text = self._format_plain_message(msg_data)
                        await self.bot.send_message(
                            chat_id=chat_id,
                            text=plain_text
                        )
                        logger.info(
                            f"Sent plain text message to chat {chat_id} "
                            f"as fallback"
                        )
                    except Exception as fallback_error:
                        logger.error(
                            f"Fallback message also failed for chat {chat_id}: "
                            f"{fallback_error}"
                        )

                # Small delay between messages to avoid rate limiting
                await asyncio.sleep(0.1)

    async def send_to_specific_chats(self, messages: List[Dict],
                                     chat_ids: List[str]):
        """Send verification code messages to specific chat IDs"""
        for msg_data in messages:
            text = self._format_verification_message(msg_data)

            for chat_id in chat_ids:
                # Only send to configured chats
                if chat_id in self.config.telegram_chat_ids:
                    try:
                        await self.bot.send_message(
                            chat_id=chat_id,
                            text=text,
                            parse_mode='HTML'
                        )
                        logger.info(
                            f"Sent verification message to specific "
                            f"chat {chat_id}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Error sending message to chat {chat_id}: {e}"
                        )

                    await asyncio.sleep(0.1)

    async def send_admin_message(self, text: str):
        """Send message to all admin chats"""
        if not self.config.telegram_admin_ids:
            logger.warning("No admin IDs configured for admin messages")
            return

        for admin_id in self.config.telegram_admin_ids:
            try:
                await self.bot.send_message(
                    chat_id=admin_id,
                    text=text,
                    parse_mode='HTML'
                )
                logger.info(f"Sent admin message to {admin_id}")
            except Exception as e:
                logger.error(f"Error sending admin message to {admin_id}: {e}")
                # Try without HTML formatting as fallback
                try:
                    await self.bot.send_message(
                        chat_id=admin_id,
                        text=text
                    )
                    logger.info(f"Sent plain text admin message to {admin_id}")
                except Exception as fallback_error:
                    logger.error(
                        f"Fallback admin message failed for {admin_id}: "
                        f"{fallback_error}"
                    )

            await asyncio.sleep(0.1)

    async def send_status_message(self, text: str):
        """Send status message (startup/shutdown) to admin chats"""
        await self.send_admin_message(text)

    async def broadcast_message(self, text: str):
        """Broadcast a message to all configured chats"""
        for chat_id in self.config.telegram_chat_ids:
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode='HTML'
                )
                logger.info(f"Broadcasted message to chat {chat_id}")
            except Exception as e:
                logger.error(f"Error broadcasting to chat {chat_id}: {e}")
                # Try without HTML formatting as fallback
                try:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=text
                    )
                    logger.info(f"Sent plain text broadcast to chat {chat_id}")
                except Exception as fallback_error:
                    logger.error(
                        f"Fallback broadcast failed for chat {chat_id}: "
                        f"{fallback_error}"
                    )

            await asyncio.sleep(0.1)

    def _format_plain_message(self, msg_data: Dict) -> str:
        """Format verification message as plain text (fallback)"""
        codes_text = ""
        if msg_data['codes']:
            codes_text = f"\n\nCodes found: {' | '.join(msg_data['codes'])}"

        # Format datetime with timezone awareness
        msg_date = msg_data['date']
        if msg_date.tzinfo is None:
            msg_date = msg_date.replace(tzinfo=timezone.utc)

        time_str = msg_date.strftime('%H:%M:%S UTC')

        text = (
            f"📧 Verification Email Received\n\n"
            f"Subject: {msg_data['subject']}\n"
            f"Time: {time_str}"
            f"{codes_text}"
        )

        return text

    def _format_verification_message(self, msg_data: Dict) -> str:
        """Format verification message for Telegram"""
        codes_text = ""
        if msg_data['codes']:
            codes_text = (
                f"\n\n🔢 <b>Codes found:</b> "
                f"<code>{' | '.join(msg_data['codes'])}</code>"
            )

        # Format datetime with timezone awareness
        msg_date = msg_data['date']
        if msg_date.tzinfo is None:
            msg_date = msg_date.replace(tzinfo=timezone.utc)

        time_str = msg_date.strftime('%H:%M:%S UTC')

        # Escape HTML entities to prevent parsing errors
        subject = html.escape(msg_data['subject'])

        text = (
            f"📧 <b>Verification Email Received</b>\n\n"
            f"📋 <b>Subject:</b> {subject}\n"
            f"🕐 <b>Time:</b> {time_str}"
            f"{codes_text}"
        )

        return text

    async def start_polling(self):
        """Start the bot polling"""
        try:
            logger.info("Starting Telegram bot polling...")
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Error in bot polling: {e}")
        finally:
            await self.bot.session.close()

    async def close(self):
        """Close bot session"""
        await self.bot.session.close()

    def is_authorized_chat(self, chat_id: str) -> bool:
        """Check if chat ID is in the authorized list"""
        return chat_id in self.config.telegram_chat_ids

    def is_admin(self, chat_id: str) -> bool:
        """Check if chat ID is in the admin list"""
        return chat_id in self.config.telegram_admin_ids
