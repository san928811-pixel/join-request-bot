import os
import logging
from telegram import Update, ChatJoinRequest
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ContextTypes

# Logging setup
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Automatically approve join requests and send welcome messages."""
    req: ChatJoinRequest = update.chat_join_request
    user = req.from_user
    chat = req.chat

    try:
        # 1️⃣ Approve join request
        await context.bot.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        log.info(f"✅ Approved join request from {user.first_name} ({user.id})")

        # 2️⃣ Send custom welcome message in channel
        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"🎉 Welcome {user.mention_html()} to *{chat.title}*! ❤️\nEnjoy your stay here!",
                parse_mode="HTML"
            )
        except Exception as e:
            log.warning(f"Cannot send message in channel: {e}")

        # 3️⃣ Send message to user's DM
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=(
                    f"👋 Hello {user.first_name}!\n\n"
                    f"✅ Your join request to *{chat.title}* has been accepted.\n"
                    f"💬 Stay active and don’t miss any updates!\n\n"
                    f"👉 Visit our special link: https://t.me/{chat.username or 'yourchannel'}"
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            log.warning(f"Cannot DM user: {e}")

    except Exception as e:
        log.error(f"❌ Failed to approve: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN:
        log.error("BOT_TOKEN not found in config vars!")
        raise SystemExit(1)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(auto_approve))

    log.info("🤖 Bot started and waiting for join requests...")
    app.run_polling()
