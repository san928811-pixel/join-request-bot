import os
import logging
from telegram import Update, ChatJoinRequest
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ContextTypes

# Logging setup
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# --- BOT TOKEN (Heroku config vars me set karo) ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    log.error("BOT_TOKEN not found. Set it in Heroku config vars.")
    raise SystemExit(1)

# --- Channel info ---
CHANNEL_NAME = "Full Open Video"
CHANNEL_LINK = "https://t.me/+Pf1Ez0N-no8zZmVi"

# --- Custom Welcome Message ---
WELCOME_TEXT = (
    "🥵 <b>Welcome🔥🔥 Zone</b>\n\n"
    "🔥 <b>Full open videos</b> unlock in <b>24 hours</b> — the wait is worth it 😉\n"
    "💋 Real entertainment, real heat — only for real ones 🥵\n"
    "👇 <b>Dive in now 👇</b>\n\n"
    f"👉 <b>{CHANNEL_NAME}</b>\n"
    f"{CHANNEL_LINK}"
)

async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-approve join request and send welcome message in DM."""
    req: ChatJoinRequest = update.chat_join_request
    user = req.from_user
    chat = req.chat

    try:
        # Approve user automatically
        await context.bot.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        log.info("Approved join request for: %s (%s)", user.first_name, user.id)
    except Exception as e:
        log.error("Approval failed for %s: %s", user.first_name, e)
        return

    # Send DM to user
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=WELCOME_TEXT,
            parse_mode="HTML"
        )
        log.info("DM sent to user %s", user.first_name)
    except Exception as e:
        log.warning("Could not DM %s: %s", user.first_name, e)


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(auto_approve))
    log.info("🤖 Bot started — waiting for join requests...")
    app.run_polling()
