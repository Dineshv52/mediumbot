import feedparser
import json
import asyncio
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)
import os
from dotenv import load_dotenv



# === CONFIGURATION ===
load_dotenv()
TELEGRAM_TOKEN = os.getenv("bot_token")
ADMIN_CHANNEL = int(os.getenv("ADMIN_CHANNEL", "0"))
LOGS_CHANNEL = int(os.getenv("LOGS_CHANNEL", "0"))
POSTED_LINKS_FILE = "posted_links.txt"
SETTINGS_FILE = "settings.json"
CHECK_INTERVAL = 3600  # in seconds (1 hour)

# === SETTINGS HANDLER ===
def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"hashtag": "hacking", "chat_id": "@your_default_channel"}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)


# === ADMIN CHECK ===
async def is_admin(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=ADMIN_CHANNEL, user_id=user_id)
        return member.status in ("creator", "administrator")
    except Exception as e:
        print(f"Admin check failed for user {user_id}: {e}")
        return False

# === TRACK ALREADY POSTED ARTICLES ===
def load_posted_links():
    try:
        with open(POSTED_LINKS_FILE, "r") as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

def save_posted_link(link):
    with open(POSTED_LINKS_FILE, "a") as f:
        f.write(link + "\n")

# === ASYNC FEED SCRAPER ===
async def check_and_post(bot: Bot):
    settings = load_settings()
    hashtag = settings["hashtag"]
    chat_id = settings["chat_id"]
    posted_links = load_posted_links()

    feed_url = f"https://medium.com/feed/tag/{hashtag}"
    feed = feedparser.parse(feed_url)

    for entry in feed.entries[:5]:
        title = entry.title
        link = entry.link

        if link not in posted_links:
            message = f"🧠 *{title}*\n\n🔗 {link}\n\n#{hashtag} #infosec #cybersecurity"
            try:
                await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
                save_posted_link(link)
            except Exception as e:
                print(f"Failed to post to {chat_id}: {e}")
                try:
                    await bot.send_message(chat_id=LOGS_CHANNEL, text=f"❌ Error posting to {chat_id}: {e}")
                except Exception as log_err:
                    print(f"Failed to log error to logs channel: {log_err}")

# === COMMAND HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Medium Feed Bot is live.\nUse /settag, /setchat, /startfeed, /stopfeed")

async def set_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(context.bot, update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    if context.args:
        settings = load_settings()
        settings["hashtag"] = context.args[0]
        save_settings(settings)
        await update.message.reply_text(f"✅ Hashtag updated to: #{context.args[0]}")
    else:
        await update.message.reply_text("⚠️ Usage: /settag <hashtag>")

async def set_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(context.bot, update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    if context.args:
        settings = load_settings()
        settings["chat_id"] = context.args[0]
        save_settings(settings)
        await update.message.reply_text(f"✅ Chat ID updated to: {context.args[0]}")
    else:
        await update.message.reply_text("⚠️ Usage: /setchat <@channelname or chat_id>")

# Feed state management
running = {"active": False}

async def start_feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(context.bot, update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    if not running["active"]:
        running["active"] = True
        await update.message.reply_text("🚀 Started scraping Medium posts every hour.")

        async def loop_feed():
            while running["active"]:
                await check_and_post(context.bot)
                await asyncio.sleep(CHECK_INTERVAL)

        context.application.create_task(loop_feed())
    else:
        await update.message.reply_text("ℹ️ Already running.")

async def stop_feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(context.bot, update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    running["active"] = False
    await update.message.reply_text("🛑 Stopped Medium feed scraping.")

# === MAIN ===
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("settag", set_tag))
    app.add_handler(CommandHandler("setchat", set_chat))
    app.add_handler(CommandHandler("startfeed", start_feed))
    app.add_handler(CommandHandler("stopfeed", stop_feed))
    print("Bot started.")
    try:
        bot = app.bot
        asyncio.get_event_loop().run_until_complete(
            bot.send_message(chat_id=LOGS_CHANNEL, text="✅ Bot has started successfully.")
        )
    except Exception as e:
        print(f"Failed to send start message to logs channel: {e}")
    print("Settings:", load_settings())
    print("Admin channel:", ADMIN_CHANNEL)    
    app.run_polling()

if __name__ == "__main__":
    main()