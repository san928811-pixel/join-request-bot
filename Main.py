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

# Logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# BOT_TOKEN must be set in Heroku config vars
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    log.error("BOT_TOKEN not set in environment variables.")
    raise SystemExit(1)

# --- Your single channel link ---
CHANNEL_NAME = "Full Open Video"
CHANNEL_LINK = "https://t.me/+Pf1Ez0N-no8zZmVi"

async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-approve join request and DM the new user with channel link."""
    req: ChatJoinRequest = update.chat_join_request
    user = req.from_user
    chat = req.chat

    try:
        # 1) Approve the join request
        await context.bot.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        log.info("Approved join request: %s (%s)", user.first_name, user.id)
    except Exception as e:
        log.error("Failed to approve join request for %s (%s): %s", user.first_name, user.id, e)
        return

    # Prepare button for DM
    keyboard = [
        [InlineKeyboardButton(f"📢 {CHANNEL_NAME}", url=CHANNEL_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # DM message text
    dm_text = (
        f"👋 Hello {user.first_name}!\n\n"
        f"✅ Your request to join *{chat.title}* has been accepted.\n\n"
        f"👇 Check out our main channel for all updates:\n"
    )

    # 2) Try to send DM to the user
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=dm_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        log.info("Sent DM to user %s (%s)", user.first_name, user.id)
    except Exception as e:
        log.warning("Could not send DM to %s (%s): %s", user.first_name, user.id, e)

    # --- Optional: Welcome message in group/channel ---
    try:
        await context.bot.send_message(
            chat_id=chat.id,
            text=(
                f"🎉 Welcome {user.mention_html()} to <b>{chat.title}</b>! ❤️\n\n"
                f"👉 Don’t forget to follow our main channel:"
            ),
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        log.info("Posted welcome message in %s", chat.title)
    except Exception as e:
        log.warning("Could not post welcome message in channel %s: %s", chat.title, e)


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(auto_approve))

    log.info("Bot started — waiting for join requests...")
    app.run_polling()
