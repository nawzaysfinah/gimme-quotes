import logging
import os
import requests
import json
import time
import random
import schedule
import telegram
import pytz
from datetime import datetime, timezone
from telegram import __version__ as TG_VER
from flask import Flask

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = Flask(__name__)

# Environment variables
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

message = None
tz = pytz.timezone("Asia/Singapore")
morning = "09:00"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hey {user.first_name}!\nWelcome to the Gimme Quotes Bot!")
    time.sleep(1)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Quotes are a great source of motivation\n" +"Hopefully with this bot you can /give and /receive some quotes and spread some love.")
    time.sleep(1.8)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Let's begin! \n\n"
    + "/give - if you want to send us a quote\n"
    + "/receive -  if you want to receive a quote\n"
    + "/about - to find out more about this bot\n"
    + "/daily - to subscribe to a daily quote\n"
    + "/help - will lead you to a help guide on how to use this bot\n")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Gimme Quotes bot is a telegram bot that send and receives quotes via telegram to a Notion database via the Notion-API \n")
    time.sleep(1)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Quotes database can be accessed at \nhttps://syaz.super.site/quotespicsmusings\n\n" +
                                   "Sample code on Github\nhttps://github.com/nawzaysfinah/gimme-quotes\n\n" +  "Credits:\nPython-Telegram-Bot, Pretty Static")
    time.sleep(1)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="How's bout a good ol' quote for you, buddy? /receive")
    time.sleep(1)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="So you need some help? I've got you :)\n"+ "To send a quote, please send them to me in the following format:\n")
    time.sleep(1)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="This is the quote./This is the author's name\n")
    time.sleep(1)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="For e.g.\n"
    + "This is an awesome inspirational quote/Author's Name\n\n")
    time.sleep(1.5)
    await context.bot.sendPhoto(chat_id=update.effective_chat.id, photo ='https://telegra.ph/file/ba54c95d6c5c83c6760cf.jpg', caption = "Here's an example of how to use the Gimme Quotes bot")
    time.sleep(2)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="If you're ready, you can start sending me quotes!")

async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="To send a quote: Please send them to me in the following format:\n"
    + "This is the quote.'/'This is the author's name'\n")
    time.sleep(2)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Alright buddy, what do you have for me?")
    time.sleep(1)

async def quote(update:Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text

    def create_page(data: dict):
        create_url = "https://api.notion.com/v1/pages"
        payload = {"parent": {"database_id" : DATABASE_ID}, "properties": data}

        res = requests.post(create_url, headers=headers, json=payload)
        print(str(res.status_code))

        return res

    pear = str(message)
    quote_in, author_in = pear.split("/")
    print("New quote!: \n\n" + quote_in)
    print("by " + author_in)

    Author =  author_in
    Quote = quote_in

    await context.bot.send_message(chat_id=update.effective_chat.id, text='"'+ Quote + '"\n' + "- " + Author)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Thank you for the quote!')
    await context.bot.send_message(chat_id=update.effective_chat.id, text='/give me another quote! or /receive a quote at random from our database?')
    published_date = datetime.now().astimezone(timezone.utc).isoformat()
    data = {
        "Author": {"title": [{"text": {"content": Author}}]},
        "Quote": {"rich_text": [{"text": {"content": Quote}}]},
        "Published": {"date": {"start": published_date, "end": None}}
    }

    create_page(data)

async def receive(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='chotomate! retrieving quote for you des...')

    readURL = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {"page_size": 100}

    res = requests.request("POST",readURL,json=payload, headers=headers)
    data = res.json()

    res_status = str(res.status_code)
    print("POST request: " + res_status)

    results = data['results']

    quotes = []
    author = []
    for result in results:
        quotes.append(result["properties"]["Quote"]["rich_text"][0]["plain_text"])
        author.append(result["properties"]["Author"]["title"][0]["plain_text"])

    quoteChoice = random.randint(0, len(quotes) - 1)
    print(quoteChoice)
    Quote_msg = str(quotes[quoteChoice])
    Author_msg = author[quoteChoice]

    await context.bot.send_message(chat_id=update.effective_chat.id, text=Quote_msg + "\n\n - " + Author_msg)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Would you like to /give another quote or /receive a new one?\n" +
                                   "Forward this quote to your friends, to share the love!")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I only respond to /start, /give, /receive or /help")

if __name__ == '__main__':
    application = Application.builder().token(API_TOKEN).build()

    start_handler = CommandHandler('start', start)
    about_handler = CommandHandler('about', about)
    help_handler = CommandHandler('help', help)
    receive_handler = CommandHandler('receive', receive)
    give_handler = CommandHandler('give', give)
    quote_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), quote)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(about_handler)
    application.add_handler(help_handler)
    application.add_handler(quote_handler)
    application.add_handler(receive_handler)
    application.add_handler(give_handler)
    application.add_handler(unknown_handler)

    application.run_polling()

schedule.every().day.at(morning).do(receive)

while True:
    schedule.run_pending()
    time.sleep(1)