import os
import time
import random
import requests
import pytz
from datetime import datetime, timezone
from telegram import Update
from telegram.ext import ContextTypes

# Environment
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

tz = pytz.timezone("Asia/Singapore")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    if user is None or chat is None:
        return
    await context.bot.send_message(chat_id=chat.id, text=f"Hey {user.first_name}!\nWelcome to the Gimme Quotes Bot!")
    time.sleep(1)
    await context.bot.send_message(chat_id=chat.id, text="Quotes are a great source of motivation\nHopefully with this bot you can /give and /receive some quotes and spread some love.")
    time.sleep(1.8)
    await context.bot.send_message(chat_id=chat.id, text="Let's begin! \n\n"
        + "/give - if you want to send us a quote\n"
        + "/receive -  if you want to receive a quote\n"
        + "/about - to find out more about this bot\n"
        + "/daily - to subscribe to a daily quote\n"
        + "/help - will lead you to a help guide on how to use this bot\n")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Gimme Quotes bot is a telegram bot that sends and receives quotes via Telegram to a Notion database via the Notion API.")
    time.sleep(1)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Quotes database: https://syaz.super.site/quotespicsmusings\nGitHub: https://github.com/nawzaysfinah/gimme-quotes\nCredits: Python-Telegram-Bot, Pretty Static")
    time.sleep(1)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="How's bout a good ol' quote for you, buddy? /receive")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="To send a quote, use the format:\nThis is the quote./This is the author's name")
    time.sleep(1)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Example:\nThis is an awesome inspirational quote/Author's Name")
    time.sleep(1.5)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://telegra.ph/file/ba54c95d6c5c83c6760cf.jpg', caption="Here's an example of how to use the Gimme Quotes bot")
    time.sleep(2)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="If you're ready, you can start sending me quotes!")

async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="To send a quote, use:\nQuote/Author format.")
    time.sleep(2)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Alright buddy, what do you have for me?")

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    try:
        quote_in, author_in = message.split("/")
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please use the format: Quote/Author")
        return

    data = {
        "Author": {"title": [{"text": {"content": author_in.strip()}}]},
        "Quote": {"rich_text": [{"text": {"content": quote_in.strip()}}]},
        "Published": {"date": {"start": datetime.now().astimezone(timezone.utc).isoformat()}}
    }

    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json={"parent": {"database_id": DATABASE_ID}, "properties": data})
    print(res.status_code)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'"{quote_in.strip()}"\n- {author_in.strip()}')
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you for the quote! /give another or /receive one?")

async def receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Retrieving quote for you...')

    res = requests.post(f"https://api.notion.com/v1/databases/{DATABASE_ID}/query", headers=headers, json={"page_size": 100})
    data = res.json()
    results = data.get("results", [])

    quotes = [r["properties"]["Quote"]["rich_text"][0]["plain_text"] for r in results if r["properties"]["Quote"]["rich_text"]]
    authors = [r["properties"]["Author"]["title"][0]["plain_text"] for r in results if r["properties"]["Author"]["title"]]

    if not quotes:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No quotes found!")
        return

    i = random.randint(0, len(quotes) - 1)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'"{quotes[i]}"\n\n– {authors[i]}')
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Would you like to /give another quote or /receive a new one?")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command. Try /start, /give, /receive or /help.")