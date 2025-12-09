# ================== IMPORTS ==================
import logging
import asyncio
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ChatJoinRequestHandler,
    ContextTypes,
    filters,
)

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# ================== CONFIG ==================
TOKEN = "8488649116:AAEJFm2x5h6S8UOccENK5kMzv00aU3Q13RU"
ADMIN_IDS = {7895892794}
BOT_USERNAME = "Joinerequest_bot"

MONGO_URI = "mongodb+srv://san928811_db_user:7OufFF7Ux8kOBnrO@cluster0.l1kszyc.mongodb.net/?appName=Cluster0"

CHANNELS = [
    ("🔥 Full Open Video", "https://t.me/+2176h2avfZQ2MWQ0"),
    ("💙 Instagram Collection", "https://t.me/+dVLzuQk-msw3MjBk"),
    ("⚡ All Influencer Viral Video", "https://t.me/+H_ExJVtnFuMxMzQ0"),
    ("🎬 Worldwide Viral Video", "https://t.me/+sBJuAWxsHiIxY2E0"),
]

# ================== SMALL UNLOCK MESSAGE ==================
UNLOCK_TEXT = (
    "🔓 *Unlock Required*\n\n"
    "👇 Full access पाने के लिए नीचे दिए गए START बटन को दबाएँ!\n\n"
    "⭐ तीन जगह START दिया है ताकि आसानी से दिख जाए:\n"
    "1️⃣ START दबाएँ और आगे बढ़ें\n"
    "2️⃣ Continue with START\n"
    "3️⃣ Please tap START to continue\n\n"
    "*English:* Tap *START NOW* button below 👇"
)

# ================== BIG WELCOME MESSAGE ==================
WELCOME_MAIN = (
    "👋 *Welcome to Viral Zone!*\n\n"
    "🔥 यहाँ आपको Daily Viral, Open & Exclusive Videos मिलेंगी!\n"
    "👇 नीचे दिए गए channels join करें 👇\n"
)

def build_links_text():
    txt = "🔗 *Important Links*\n\n"
    for name, link in CHANNELS:
        txt += f"• *{name}*\n{link}\n\n"
    return txt

def start_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("▶️ START NOW", url=f"https://t.me/{BOT_USERNAME}?start=start")]]
    )

# ================== DB ==================
client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client["join_req_system"]
users_col = db["users"]
broadcasts_col = db["broadcasts"]

# ================== LOGGING ==================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BOT")

# ================== HELPERS ==================
def is_admin(uid): return uid in ADMIN_IDS

def save_user(u):
    now = datetime.utcnow()
    users_col.update_one(
        {"user_id": u.id},
        {
            "$set": {
                "first_name": u.first_name,
                "username": u.username,
                "active": True,
                "last_active": now,
            },
            "$setOnInsert": {"joined_at": now},
        },
        upsert=True,
    )

def get_active_users():
    return [u["user_id"] for u in users_col.find({"active": True})]

def mark_inactive(uid):
    users_col.update_one({"user_id": uid}, {"$set": {"active": False}})

# ================== JOIN REQUEST ==================
async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    user = req.from_user

    try:
        await req.approve()
    except:
        return

    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=UNLOCK_TEXT,
            parse_mode="Markdown",
            reply_markup=start_keyboard(),
        )
    except Exception as e:
        log.warning(f"Cannot DM user {user.id}: {e}")

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)

    await update.message.reply_text(WELCOME_MAIN, parse_mode="Markdown")
    await update.message.reply_text(build_links_text(), parse_mode="Markdown")

# ================== PANEL ==================
admin_keyboard = ReplyKeyboardMarkup(
    [
        ["📊 Active Users", "📈 Today Joined"],
        ["👥 Total Users"],
        ["📢 Broadcast", "📤 Forward Broadcast"],
        ["🧹 Delete All", "❌ Cancel"],
    ],
    resize_keyboard=True,
)

async def panel(update, context):
    if not is_admin(update.effective_user.id): return
    await update.message.reply_text("🛠 *ADMIN PANEL*", parse_mode="Markdown", reply_markup=admin_keyboard)

async def cancel(update, context):
    context.user_data.clear()
    await update.message.reply_text("❌ Broadcast Mode OFF", reply_markup=admin_keyboard)

# ================== BROADCAST ==================
async def run_broadcast(context, users, msgs, reply_msg):
    sent, fail = 0, 0
    for uid in users:
        try:
            for m in msgs:
                await m.copy(chat_id=uid)
            sent += 1
        except:
            fail += 1
            mark_inactive(uid)
        await asyncio.sleep(0.05)

    await reply_msg.reply_text(f"📢 Broadcast Completed!\n✔ Sent: {sent}\n❌ Failed: {fail}")

async def delete_all(update, context):
    deleted = 0
    for d in broadcasts_col.find({}):
        try:
            await context.bot.delete_message(d["chat_id"], d["message_id"])
            deleted += 1
        except:
            pass
    broadcasts_col.delete_many({})
    await update.message.reply_text(f"🧹 Deleted: {deleted}")

# ================== TEXT ROUTER ==================
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = update.effective_user

    if not is_admin(user.id): return
    text = msg.text

    if context.user_data.get("mode") == "broadcast":
        if "msgs" not in context.user_data:
            context.user_data["msgs"] = []

        if text.lower() == "done":
            users = get_active_users()
            msgs = context.user_data.pop("msgs", [])
            context.user_data["mode"] = None
            await msg.reply_text("📢 Broadcasting started…")
            asyncio.create_task(run_broadcast(context, users, msgs, msg))
            return

        context.user_data["msgs"].append(msg)
        await msg.reply_text("📩 Saved! Type DONE when finished.")
        return

    if text == "📊 Active Users":
        await msg.reply_text(f"👥 Active: {len(get_active_users())}")

    elif text == "📈 Today Joined":
        today = datetime.utcnow().date()
        count = users_col.count_documents({"joined_at": {"$gte": datetime(today.year, today.month, today.day)}})
        await msg.reply_text(f"📆 Today: {count}")

    elif text == "👥 Total Users":
        await msg.reply_text(f"📌 Total: {users_col.count_documents({})}")

    elif text in ("📢 Broadcast", "📤 Forward Broadcast"):
        context.user_data["mode"] = "broadcast"
        context.user_data["msgs"] = []
        await msg.reply_text("📢 Broadcast Mode ON\nSend messages then type DONE.")

    elif text == "🧹 Delete All":
        await delete_all(update, context)

    elif text == "❌ Cancel":
        await cancel(update, context)

# ================== RUN ==================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(ChatJoinRequestHandler(join_request))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, text_router))

    print("BOT RUNNING…")
    app.run_polling()
