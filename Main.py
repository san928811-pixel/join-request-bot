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

# --- Channels info ---
CHANNELS = [
    {
        "name": "Full Open Video",
        "link": "https://t.me/+cfT4dxwQeONiMTk1"
    },
    {
        "name": "All Instagram Viral Election",
        "link": "https://t.me/+XMc2zKQCFhg1Njdl"   # ✅ Updated 2nd link
    },
    {
        "name": "All Influencer Viral Video",
        "link": "https://t.me/+mQsqgOIRQrkyOGM0"
    },
    {
        "name": "All Worldwide Viral Video",
        "link": "https://t.me/+1Juo8taiI9FhMzQ1"   # ✅ Updated 4th link
    }
]

# --- Custom Welcome Message ---
def make_welcome_text():
    text = (
        "🥵 <b>Welcome🔥🔥 Zone</b>\n\n"
        "🔥 <b>Full open videos</b> unlock in <b>24 hours</b> — the wait is worth it 😉\n"
        "💋 Real entertainment, real heat — only for real ones 🥵\n"
        "👇 <b>Dive in now 👇</b>\n\n"
    )
    for c in CHANNELS:
        text += f"👉 <b>{c['name']}</b>\n{c['link']}\n\n"
    return text.strip()

WELCOME_TEXT = make_welcome_text()


async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-approve join request and send welcome message in DM."""
    req: ChatJoinRequest = update.chat_join_request
    user = req.from_user
    chat = req.chat

    try:
        await context.bot.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        log.info("Approved join request for: %s (%s)", user.first_name, user.id)
    except Exception as e:
        log.error("Approval failed for %s: %s", user.first_name, e)
        return

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
