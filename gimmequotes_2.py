import logging
# from telegram import Update
from telegram.ext import filters, ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes
import requests
import notion_client
from notion_client import Client
from datetime import datetime, timezone
import os
import json # to PARSE JSON string to return values
# import random # to randomise quotes selected from database
# import itertools
import time #to add delay to telegram bot

from telegram import __version__ as TG_VER
from setup import GIMME, TEST, NOTION_TOKEN, DATABASE_ID

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

#to start Flask WebApp
from flask import Flask, request

app = Flask(__name__)

# Declare variables
# declared in setup.py
API_TOKEN = TEST
NOTION_TOKEN # This is the token for your notion API
DATABASE_ID # This is the database ID of where your quotes are stored

# # Create an Updater instance using the telegram API token
# updater = Updater(token=API_TOKEN, use_context=True)
# dispatcher = updater.dispatcher

headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

message = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! Welcome to the Gimme Quotes Bot!\nDo you have quotes for me?")
    time.sleep(1)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please send them to me in the following format:\n'This is the quote.'/'This is the author's name'")
    time.sleep(1)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="e.g.\n" 
    + "This is an awesome inspirational quote/Author's Name\n\n")
    time.sleep(1.5)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="If you're ready, you can start sending me quotes!")


async def quote(update:Update, context: ContextTypes.DEFAULT_TYPE):
# Collect the message
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
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Send me another quote! or /call a quote at random from our database?')
    published_date = datetime.now().astimezone(timezone.utc).isoformat()
    data = {
        "Author": {"title": [{"text": {"content": Author}}]},
        "Quote": {"rich_text": [{"text": {"content": Quote}}]},
        "Published": {"date": {"start": published_date, "end": None}}
    }

    create_page(data)

#need to write new command handler to return code from notion database at random with Quote & Author.
async def call(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='chotomate! retrieving quote for you des...')
    
    # def get_pages(num_pages=None):
    readURL = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    num_pages = None
    get_all = num_pages is None
    page_size = 100 if get_all else num_pages
    payload = {"page_size": page_size}

    #add a filter to return only the filtered quote called #payload_1quote, worked for awhile but stopped working
    payload_1quote = {
        "filter": {
            "property": "Chosen item",
            "checkbox": {
                "equals": True
            }
        }
    }   

    res = requests.request("POST",readURL,json=payload, headers=headers) #change json to filter for correct things
    data = res.json()


    res_status = str(res.status_code)
    print("POST request: " + res_status)
    # print("JSON string is: " + res.text)

    # # Code below is to dump JSON data into a .json file to be analyzed. 
    # with open('./db.json', 'w', encoding = 'utf8') as f:
    #     json.dump(data, f, ensure_ascii=False)

    # this is to the retrieve the results from the JSON string
    results = data['results']

    quotes = []
    author = []
    for result in results:
        # print(result["properties"]["Quote"]["rich_text"][0]["plain_text"]) # this prints it all
        """
        quotes = result["properties"]["Quote"]["rich_text"][0]["plain_text"] # this is a string, each line separated by 
        author = result["properties"]["Author"]["title"][0]["plain_text"]
        """
        quotes.append(result["properties"]["Quote"]["rich_text"][0]["plain_text"])
        author.append(result["properties"]["Author"]["title"][0]["plain_text"])
        
        # print(quotes)
        # print(author)

    # ======== Will print the Quote at index 12 ========
    import random
    quoteChoice = random.randint(0, len(quotes)) # pick a random number between 0 and the number of available quotes
    print(quoteChoice) # prints the selected random number
    Quote_msg = str(quotes[quoteChoice]) # picks the quote at index of the random number generated
    Author_msg = author[quoteChoice] # picks the author at index of the random number generated

    await context.bot.send_message(chat_id=update.effective_chat.id, text=Quote_msg + "\n\n - " + Author_msg)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Would you like to send another quote or /call a new one?")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I only respond to /start or /call")


#declare ApplicationBuilder & Handlers below
if __name__ == '__main__':
    application = ApplicationBuilder().token(API_TOKEN).build()

    start_handler = CommandHandler('start', start)
    call_handler = CommandHandler('call', call)
    quote_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), quote)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(quote_handler)
    application.add_handler(call_handler)
    application.add_handler(unknown_handler)

    application.run_polling()

    # https://api.telegram.org/bot5912247638:AAHo1kYgW2c6TWiOuJAlWuSfKouzoVAFTQE/setWebhook?url=https://git.heroku.com/gimmequotes.git

import os

# TOKEN = os.getenv('BOTAPIKEY') # to set the telegram bot api key within codecapsules, so api key isnt visible on github

# PORT = int(os.environ.get('PORT', '8443'))
# HOOK_URL = 'your-codecapsules-url-here' + '/' + TOKEN

# # add handlers
# application.run_webhook(
#     listen="0.0.0.0",
#     port=PORT,
#     url_path=TOKEN,
#     webhook_url=HOOK_URL
# )