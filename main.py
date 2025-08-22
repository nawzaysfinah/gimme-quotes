# main.py
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from setup import GIMME
from handlers import start, about, help, give, receive, quote, unknown

app = Flask(__name__)

application = ApplicationBuilder().token(GIMME).build()

# Add all Telegram command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("about", about))
application.add_handler(CommandHandler("help", help))
application.add_handler(CommandHandler("give", give))
application.add_handler(CommandHandler("receive", receive))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), quote))
application.add_handler(MessageHandler(filters.COMMAND, unknown))

# Webhook endpoint that Telegram hits when a message is received
@app.route(f"/{GIMME}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

# Optional route to manually set the webhook
@app.route("/set_webhook")
def set_webhook():
    # Automatically resolves Render's external hostname
    base_url = request.host_url.rstrip("/")
    webhook_url = f"{base_url}/{GIMME}"
    success = application.bot.set_webhook(url=webhook_url)
    return f"Webhook set: {success}"