from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os
GIMME = os.getenv("GIMME")
from handlers import start, about, help, give, receive, quote, unknown

app = Flask(__name__)
application = None  # Global app instance for reuse

async def setup_telegram_app():
    global application
    if not application:
        if not GIMME:
            raise ValueError("Missing GIMME environment variable.")
        application = (
            ApplicationBuilder()
            .token(GIMME)
            .build()
        )
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("about", about))
        application.add_handler(CommandHandler("help", help))
        application.add_handler(CommandHandler("give", give))
        application.add_handler(CommandHandler("receive", receive))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), quote))
        application.add_handler(MessageHandler(filters.COMMAND, unknown))
        await application.initialize()  # PREPARE app for webhook
        await application.start()       # START without polling

@app.route(f"/{GIMME}", methods=["POST"])
async def telegram_webhook():
    await setup_telegram_app()
    assert application is not None
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

@app.route("/set_webhook")
async def set_webhook():
    await setup_telegram_app()
    assert application is not None
    webhook_url = f"{request.host_url.rstrip('/')}/{GIMME}"
    success = await application.bot.set_webhook(url=webhook_url)
    return f"Webhook set: {success}"