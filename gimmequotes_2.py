import logging
from telegram.ext import filters, ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes
import requests
import notion_client
from notion_client import Client
from datetime import datetime, timezone
import os
import json # to PARSE JSON string to return values
import time # to add delay to telegram bot
import random # to randomly select quote from Notion database
import schedule # to create a schedule of posting
import time
import telegram

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
# Declared in setup.py
API_TOKEN = TEST
NOTION_TOKEN # This is the token for your notion API
DATABASE_ID # This is the database ID of where your quotes are stored

headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

message = None

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
    await context.bot.send_message(chat_id=update.effective_chat.id, text="This is the quote.'/'This is the author's name'\n")
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
# Collect the message
    message = update.message.text
    if len(message) > 3:
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
        
    else:
        if update.message.text == "Yes":
            
            send_time = "09:00:00"
            schedule.every().day.at(send_time).do(receive)
            
            def start_scheduler():
                while True:
                    schedule.run_pending()
                    time.sleep(1)

            start_scheduler()  
        
        else: 
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Message scheduler remains off")



async def daily(update:Update, context:ContextTypes.DEFAULT_TYPE):     
    DECISION = range(1)
    # Schedule a message everyday at 9:00 AM
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="Do you want to turn on the message scheduler?")
    reply_keyboard = [["Yes", "No"]]
    
    await update.message.reply_text(
        "Do you want to turn on the message scheduler?",
        
        reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Yes or no?"
        ),
    )
    return DECISION

# Command handler to return code from notion database at random with Quote & Author.
async def receive(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='chotomate! retrieving quote for you des...')
    
    # def get_pages(num_pages=None):
    readURL = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    num_pages = None
    get_all = num_pages is None
    page_size = 100 if get_all else num_pages
    payload = {"page_size": page_size}

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
        quotes = result["properties"]["Quote"]["rich_text"][0]["plain_text"]
        author = result["properties"]["Author"]["title"][0]["plain_text"]
        """
        quotes.append(result["properties"]["Quote"]["rich_text"][0]["plain_text"])
        author.append(result["properties"]["Author"]["title"][0]["plain_text"])

    quoteChoice = random.randint(0, len(quotes)) # pick a random number between 0 and the number of available quotes
    print(quoteChoice) # prints the selected random number
    Quote_msg = str(quotes[quoteChoice]) # picks the quote at index of the random number generated
    Author_msg = author[quoteChoice] # picks the author at index of the random number generated

    await context.bot.send_message(chat_id=update.effective_chat.id, text=Quote_msg + "\n\n - " + Author_msg)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Would you like to /give another quote or /receive a new one?\n" + 
                                   "Forward this quote to your friends, to share the love!")
    


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I only respond to /start, /give, /receive or /help")


# Declare ApplicationBuilder & Handlers below
if __name__ == '__main__':
    application = ApplicationBuilder().token(API_TOKEN).build()

    start_handler = CommandHandler('start', start)
    about_handler = CommandHandler('about', about)
    help_handler = CommandHandler('help', help)
    receive_handler = CommandHandler('receive', receive)
    give_handler = CommandHandler('give', give)
    quote_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), quote)
    daily_handler = CommandHandler('daily', daily)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    

    application.add_handler(start_handler)
    application.add_handler(about_handler)
    application.add_handler(help_handler)
    application.add_handler(quote_handler)
    application.add_handler(receive_handler)
    application.add_handler(give_handler)
    application.add_handler(daily_handler)
    application.add_handler(unknown_handler)
    
    

    application.run_polling()

    # https://api.telegram.org/bot5912247638:AAHo1kYgW2c6TWiOuJAlWuSfKouzoVAFTQE/setWebhook?url=https://git.heroku.com/gimmequotes.git

# WIP Webhook
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