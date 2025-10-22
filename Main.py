import os
import logging
from telegram import Update, ChatJoinRequest
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ContextTypes

# Logging setup
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Automatically approve all join requests and send welcome message."""
    req: ChatJoinRequest = update.chat_join_request
    user = req.from_user
    chat = req.chat

    try:
        # Approve request
        await context.bot.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        log.info(f"✅ Approved join request from {user.first_name} ({user.id})")

        # Try sending a welcome message in channel
        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"🎉 Welcome {user.mention_html()}!",
                parse_mode="HTML"
            )
        except Exception as e:
            log.warning(f"Cannot post in channel: {e}")

        # Optional: send DM
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=f"✅ Your join request to *{chat.title}* has been approved!",
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

    log.info("🤖 Bot started and listening for join requests...")
    app.run_polling()
