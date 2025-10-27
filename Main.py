import os
import logging
from telegram import Update, ChatJoinRequest
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ContextTypes

# Logging setup
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Your bot token (replace with your real token)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    log.error("BOT_TOKEN not found. Set it in Heroku config vars.")
    raise SystemExit(1)

# --- Your single channel ---
CHANNEL_NAME = "Full Open Video"
CHANNEL_LINK = "https://t.me/+Pf1Ez0N-no8zZmVi"

# --- Custom welcome message ---
WELCOME_TEXT = (
    "👋 <b>Welcome!</b>\n\n"
    "🕒 Just joined our group — full open videos will arrive after <b>24 hours!</b>\n"
    "🔥 This is the <b>real masala zone</b> — don’t miss it! 😏🥵👇\n\n"
    f"👉 <a href='{CHANNEL_LINK}'>{CHANNEL_NAME}</a>"
)

async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-approve join request and send welcome message + link."""
    req: ChatJoinRequest = update.chat_join_request
    user = req.from_user
    chat = req.chat

    try:
        # Approve join request
        await context.bot.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        log.info("Approved join request: %s (%s)", user.first_name, user.id)
    except Exception as e:
        log.error("Approval failed for %s: %s", user.first_name, e)
        return

    # Try sending message to user's DM
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=WELCOME_TEXT,
            parse_mode="HTML"
        )
        log.info("Sent DM to %s", user.first_name)
    except Exception as e:
        log.warning("DM failed for %s: %s", user.first_name, e)

    # Optional: also send in group/channel
    try:
        await context.bot.send_message(
            chat_id=chat.id,
            text=f"🎉 Welcome {user.mention_html()}!\n\n{WELCOME_TEXT}",
            parse_mode="HTML"
        )
        log.info("Posted welcome in %s", chat.title)
    except Exception as e:
        log.warning("Welcome post failed in %s: %s", chat.title, e)


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(auto_approve))
    log.info("Bot started — waiting for join requests...")
    app.run_polling()
