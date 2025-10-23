import os
import logging
from telegram import (
    Update,
    ChatJoinRequest,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    ChatJoinRequestHandler,
    ContextTypes
)

# Logging setup
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    log.error("BOT_TOKEN missing in environment variables!")
    raise SystemExit(1)

# --- Tumhare channel links ---
CHANNEL_1_NAME = "Viral Video"
CHANNEL_1_LINK = "https://t.me/+M1zWzeJgYUFjMGI8"

CHANNEL_2_NAME = "All New Video"
CHANNEL_2_LINK = "https://t.me/+qNjhLVZ_Jh4yYWQ0"


async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req: ChatJoinRequest = update.chat_join_request
    user = req.from_user
    chat = req.chat

    try:
        await context.bot.approve_chat_join_request(chat.id, user.id)
        log.info(f"✅ Approved {user.first_name} ({user.id})")
    except Exception as e:
        log.error(f"❌ Failed to approve {user.first_name}: {e}")
        return

    # DM buttons
    buttons = [
        [InlineKeyboardButton(f"📢 {CHANNEL_1_NAME}", url=CHANNEL_1_LINK)],
        [InlineKeyboardButton(f"🎬 {CHANNEL_2_NAME}", url=CHANNEL_2_LINK)],
    ]
    markup = InlineKeyboardMarkup(buttons)

    # DM message
    message = (
        f"👋 Hello {user.first_name}!\n\n"
        f"✅ Your request to join *{chat.title}* has been accepted.\n"
        "👇 Join our other channels for more updates:"
    )

    # Send DM
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=message,
            parse_mode="Markdown",
            reply_markup=markup
        )
        log.info(f"💌 Sent DM to {user.first_name}")
    except Exception as e:
        log.warning(f"⚠️ Cannot DM {user.first_name}: {e}")


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(auto_approve))
    log.info("🤖 Bot is running and waiting for join requests...")
    app.run_polling()
