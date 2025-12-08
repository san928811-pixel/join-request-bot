import logging
from datetime import datetime, timedelta

from telegram import Update, ChatJoinRequest, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    ChatJoinRequestHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================== CONFIG ==================

BOT_TOKEN = "8488649116:AAEJFm2x5h6S8UOccENK5kMzv00aU3Q13RU"
ADMIN_IDS = {7895892794}

MONGO_URI = "mongodb+srv://san928811_db_user:7OufFF7Ux8kOBnrO@cluster0.l1kszyc.mongodb.net/?appName=Cluster0"

# ================== DB ==================

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client["old_bot_broadcast"]
users_col = db["users"]
broadcasts_col = db["broadcasts"]

# ================== LOGGING ==================

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ================== CHANNEL LINKS ==================

CHANNELS = [
    {"name": "Full Open Video", "link": "https://t.me/+2176h2avfZQ2MWQ0"},
    {"name": "All Instagram Viral Election", "link": "https://t.me/+dVLzuQk-msw3MjBk"},
    {"name": "All Influencer Viral Video", "link": "https://t.me/+H_ExJVtnFuMxMzQ0"},
    {"name": "All Worldwide Viral Video", "link": "https://t.me/+sBJuAWxsHiIxY2E0"},
]

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

# ================== HELPERS ==================

def is_admin(uid): return uid in ADMIN_IDS

def save_user(u):
    if not u: return
    users_col.update_one(
        {"user_id": u.id},
        {"$set": {
            "first_name": u.first_name,
            "username": u.username,
            "active": True,
            "last_active": datetime.utcnow(),
            "joined_at": datetime.utcnow()
        }},
        upsert=True
    )

def mark_inactive(uid):
    users_col.update_one({"user_id": uid}, {"$set": {"active": False}})

def get_active_users():
    return [u["user_id"] for u in users_col.find({"active": True})]

def count_active(): return users_col.count_documents({"active": True})

def count_today():
    today = datetime.utcnow().date()
    start = datetime(today.year, today.month, today.day)
    end = start + timedelta(days=1)
    return users_col.count_documents({"joined_at": {"$gte": start, "$lt": end}, "active": True})

# ================== ADMIN PANEL ==================

admin_keyboard = ReplyKeyboardMarkup(
    [
        ["📊 Active Users", "📈 Today Joined"],
        ["📢 Broadcast", "📤 Forward Broadcast"],
        ["🧹 Delete All", "❌ Cancel"],
    ],
    resize_keyboard=True,
)

# ================== HANDLERS ==================

async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req: ChatJoinRequest = update.chat_join_request
    u = req.from_user

    try:
        await context.bot.approve_chat_join_request(chat_id=req.chat.id, user_id=u.id)
    except:
        return

    save_user(u)

    try:
        await context.bot.send_message(chat_id=u.id, text=WELCOME_TEXT, parse_mode="HTML")
    except:
        pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    save_user(u)

    await update.message.reply_text("🔥 Welcome Back!", reply_markup=ReplyKeyboardRemove())


async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    await update.message.reply_text("🛠 ADMIN PANEL", reply_markup=admin_keyboard)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("mode", None)
    await update.message.reply_text("❌ Broadcast Mode OFF", reply_markup=admin_keyboard)


async def delete_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deleted = 0
    for d in broadcasts_col.find({}):
        try:
            await context.bot.delete_message(d["chat_id"], d["message_id"])
            deleted += 1
        except:
            pass
    broadcasts_col.delete_many({})
    await update.message.reply_text(f"🧹 Deleted: {deleted}", reply_markup=admin_keyboard)


async def do_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    users = get_active_users()

    sent = 0
    fail = 0

    for uid in users:
        try:
            sent_msg = await msg.copy(chat_id=uid)
            broadcasts_col.insert_one({"chat_id": uid, "message_id": sent_msg.message_id})
            sent += 1
        except:
            fail += 1
            mark_inactive(uid)

    await msg.reply_text(
        f"📢 Broadcast Done\n✔ Sent: {sent}\n❌ Failed: {fail}",
        reply_markup=admin_keyboard,
    )


async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    u = update.effective_user
    save_user(u)

    if not is_admin(u.id): return

    mode = context.user_data.get("mode")

    if mode == "broadcast":
        await do_broadcast(update, context)
        return

    text = msg.text

    if text == "📊 Active Users":
        await msg.reply_text(f"👥 Active Users: {count_active()}")

    elif text == "📈 Today Joined":
        await msg.reply_text(f"📆 Today Joined: {count_today()}")

    elif text in ("📢 Broadcast", "📤 Forward Broadcast"):
        context.user_data["mode"] = "broadcast"
        await msg.reply_text("📢 Broadcast Mode ON", reply_markup=admin_keyboard)

    elif text == "🧹 Delete All":
        await delete_all(update, context)

# ================== MAIN ==================

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(ChatJoinRequestHandler(auto_approve))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CommandHandler("cancel", cancel))

    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, text_router))

    print("BOT RUNNING…")
    app.run_polling()
