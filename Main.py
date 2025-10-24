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

# 🔐 Yahan apna BOT TOKEN daalo (BotFather se mila hua)
BOT_TOKEN = " 8436733857:AAEp7Jlgiq3qoKe51lwiICYKdGly3l1TLR8 "  # ← bas yahan token paste karna hai


# Logging setup
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# --- Aapka channel link aur name ---
CHANNEL_NAME = "🎬 Full Open Video"
CHANNEL_LINK = "https://t.me/+Pf1Ez0N-no8zZmVi"


async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto approve join requests and send DM to user."""
    req: ChatJoinRequest = update.chat_join_request
    user = req.from_user
    chat = req.chat

    try:
        # Approve join request
        await context.bot.approve_chat_join_request(chat.id, user.id)
        log.info(f"✅ Approved {user.first_name} ({user.id})")
    except Exception as e:
        log.error(f"❌ Failed to approve {user.first_name}: {e}")
        return

    # Create DM button
    button = [[InlineKeyboardButton(CHANNEL_NAME, url=CHANNEL_LINK)]]
    markup = InlineKeyboardMarkup(button)

    # DM message
    message = (
        f"👋 Hello {user.first_name}!\n\n"
        f"✅ Your request to join *{chat.title}* has been accepted.\n\n"
        "👇 Check out our main channel for more exclusive videos:"
    )

    # Send DM to user
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
