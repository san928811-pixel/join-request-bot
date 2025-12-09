# ================== IMPORTS ==================
import logging
import asyncio
from datetime import datetime, timedelta

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ChatJoinRequestHandler,
)

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# ================== CONFIG ==================
BOT_TOKEN = "8488649116:AAEJFm2x5h6S8UOccENK5kMzv00aU3Q13RU"
ADMIN_IDS = {7895892794}
BOT_USERNAME = "Joinerequest_bot"   # <-- YOUR BOT USERNAME

MONGO_URI = (
    "mongodb+srv://san928811_db_user:7OufFF7Ux8kOBnrO"
    "@cluster0.l1kszyc.mongodb.net/?appName=Cluster0"
)

# ================== DB ==================
client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client["old_bot_broadcast"]
users_col = db["users"]
broadcasts_col = db["broadcasts"]

# ================== LOGGING ==================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ================== CHANNEL LINKS ==================
CHANNELS = [
    ("🔥 Open Video", "https://t.me/+2176h2avfZQ2MWQ0"),
    ("💙 Instagram Viral", "https://t.me/+dVLzuQk-msw3MjBk"),
    ("⚡ Influencer Viral", "https://t.me/+H_ExJVtnFuMxMzQ0"),
    ("🎬 Worldwide Viral", "https://t.me/+sBJuAWxsHiIxY2E0"),
]

WELCOME_TEXT = (
    "👋 *Welcome to Viral Zone!*\n\n"
    "🔥 यहाँ आपको Daily Viral, Open & Exclusive Videos मिलेंगी!\n"
    "👇 नीचे दिए गए channels join करें 👇\n"
)

UNLOCK_TEXT = (
    "🔓 *Unlock Required*\n\n"
    "👇 Full access पाने के लिए नीचे दिए गए *START* बटन को दबाएँ!\n\n"
    "⭐ तीन जगह START दिया है ताकि आसानी से दिख जाए:\n"
    "1️⃣ START दबाएँ और आगे बढ़ें\n"
    "2️⃣ Continue with START\n"
    "3️⃣ Please tap START to continue\n\n"
    "*English:* Tap START NOW button below 👇"
)

# ================== HELPERS ==================
def is_admin(uid): return uid in ADMIN_IDS

def upsert_user(u):
    if not u: return
    now = datetime.utcnow()
    users_col.update_one(
        {"user_id": u.id},
        {
            "$set": {
                "first_name": u.first_name,
                "username": u.username,
                "last_active": now,
                "active": True,
            },
            "$setOnInsert": {"joined_at": now},
        },
        upsert=True,
    )

def mark_inactive(uid): users_col.update_one({"user_id": uid}, {"$set": {"active": False}})

def get_active_users(): return [x["user_id"] for x in users_col.find({"active": True})]

def count_active(): return users_col.count_documents({"active": True})
def count_total(): return users_col.count_documents({})
def count_today():
    today = datetime.utcnow().date()
    start = datetime(today.year, today.month, today.day)
    end = start + timedelta(days=1)
    return users_col.count_documents({"joined_at": {"$gte": start, "$lt": end}, "active": True})

# ================== MESSAGE BUILDERS ==================
def build_links_text():
    t = "🔗 *Important Links:*\n\n"
    for name, link in CHANNELS:
        t += f"• {name} – {link}\n"
    return t

def start_button_keyboard():
    url = f"https://t.me/{BOT_USERNAME}?start=start"
    return InlineKeyboardMarkup([[InlineKeyboardButton("▶️ START NOW", url=url)]])

async def send_full_welcome(uid, context):
    try:
        await context.bot.send_message(uid, WELCOME_TEXT, parse_mode="Markdown")
        await context.bot.send_message(uid, build_links_text(), parse_mode="Markdown")
    except Exception as e:
        log.warning(f"Full welcome failed for {uid}: {e}")

# ================== JOIN REQUEST HANDLER ==================
async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    user = req.from_user

    try:
        await req.approve()
    except:
        return

    # Send small unlock message (counting will happen ONLY after pressing start)
    try:
        await context.bot.send_message(
            user.id,
            UNLOCK_TEXT,
            parse_mode="Markdown",
            reply_markup=start_button_keyboard(),
        )
    except Exception as e:
        log.warning(f"Unlock msg failed: {e}")

# ================== START HANDLER ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_user(user)
    await send_full_welcome(user.id, context)

# ================== ADMIN PANEL ==================
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
    await update.message.reply_text("🛠 ADMIN PANEL", reply_markup=admin_keyboard)

async def cancel(update, context):
    context.user_data.clear()
    await update.message.reply_text("❌ Broadcast OFF", reply_markup=admin_keyboard)

# ================== DELETE ALL BROADCAST ==================
async def delete_all(update, context):
    bot = context.bot
    deleted = 0
    for doc in broadcasts_col.find({}):
        try:
            await bot.delete_message(doc["chat_id"], doc["message_id"])
            deleted += 1
        except:
            pass
    broadcasts_col.delete_many({})
    await update.message.reply_text(f"🧹 Deleted: {deleted}")

# ================== BROADCAST ENGINE ==================
async def run_broadcast(context, users, msgs, reply_msg):
    sent = 0; fail = 0
    for uid in users:
        try:
            for m in msgs:
                await m.copy(chat_id=uid)
            sent += 1
        except:
            fail += 1
            mark_inactive(uid)
        await asyncio.sleep(0.05)
    await reply_msg.reply_text(f"📢 Done!\n✔ {sent}\n❌ {fail}")

# ================== TEXT ROUTER ==================
async def text_router(update, context):
    msg = update.message
    user = update.effective_user

    # Update last seen ONLY for already-started users
    users_col.update_one(
        {"user_id": user.id, "active": True},
        {"$set": {"last_active": datetime.utcnow()}},
    )

    if not is_admin(user.id):
        return

    mode = context.user_data.get("mode")

    # =========== Broadcast Mode ===========
    if mode == "broadcast":
        msgs = context.user_data.get("msgs", [])

        if msg.text and msg.text.lower() == "done":
            context.user_data.clear()
            users = get_active_users()
            await msg.reply_text("📢 Broadcasting…")
            asyncio.create_task(run_broadcast(context, users, msgs, msg))
            return

        msgs.append(msg)
        context.user_data["msgs"] = msgs

        await msg.reply_text(f"Saved {len(msgs)} messages. Type DONE when ready.")
        return

    # =========== Admin Menu ===========
    txt = msg.text

    if txt in ("📢 Broadcast", "📤 Forward Broadcast"):
        context.user_data["mode"] = "broadcast"
        context.user_data["msgs"] = []
        await msg.reply_text("📢 Broadcast Mode ON\nSend messages…")
        return

    if txt == "📊 Active Users":
        await msg.reply_text(f"Active Users: {count_active()}")
    elif txt == "📈 Today Joined":
        await msg.reply_text(f"Today: {count_today()}")
    elif txt == "👥 Total Users":
        await msg.reply_text(f"Total Users: {count_total()}")
    elif txt == "🧹 Delete All":
        await delete_all(update, context)
    elif txt == "❌ Cancel":
        await cancel(update, context)

# ================== RUN BOT ==================
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(ChatJoinRequestHandler(auto_approve))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CommandHandler("cancel", cancel))

    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, text_router))

    print("BOT RUNNING…")
    app.run_polling()
