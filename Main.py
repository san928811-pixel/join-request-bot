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

# ✅ Logging setup
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# 🔐 Telegram Bot Token
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# 🔗 Tumhare 2 channels ke links yahan fit kiye gaye hain
CHANNEL_1_NAME = "Viral Video"
CHANNEL_1_LINK = "https://t.me/+M1zWzeJgYUFjMGI8"

CHANNEL_2_NAME = "All New Video"
CHANNEL_2_LINK = "https://t.me/+qNjhLVZ_Jh4yYWQ0"

# 🚀 Function: Auto approve & send welcome message with 2 channel links
async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req: ChatJoinRequest = update.chat_join_request
    user = req.from_user
    chat = req.chat

    try:
        # ✅ Approve join request
        await context.bot.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        log.info(f"✅ Approved join request from {user.first_name} ({user.id})")

        # 🔘 Buttons (2 channels)
        keyboard = [
            [InlineKeyboardButton(f"📢 {CHANNEL_1_NAME}", url=CHANNEL_1_LINK)],
            [InlineKeyboardButton(f"🎬 {CHANNEL_2_NAME}", url=CHANNEL_2_LINK)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # 💬 Send welcome message in channel/group
        await context.bot.send_message(
            chat_id=chat.id,
            text=(
                f"🎉 Welcome {user.mention_html()} to <b>{chat.title}</b>! ❤️\n\n"
                f"👇 Check out our other channels below:"
            ),
            parse_mode="HTML",
            reply_markup=reply_markup
        )

    except Exception as e:
        log.error(f"❌ Failed to approve join request: {e}")


# 🏁 Start Bot
if __name__ == "__main__":
    if not BOT_TOKEN:
        log.error("BOT_TOKEN not found in config vars!")
        raise SystemExit(1)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(auto_approve))

    log.info("🤖 Bot started and waiting for join requests...")
    app.run_polling()
