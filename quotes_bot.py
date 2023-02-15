import telegram
import json
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from notion_client import Client
import random
import os
from datetime import datetime, timezone

# BASE_URL = 'https://nawzaysfinah.pythonanywhere.com/'

# payload = {'input': 'SUBSCRIBE TO ME'}
# response = requests.get(BASE_URL, params=payload)

# json_values = response.json()

# rq_input = json_values['input']
# timestamp = json_values['timestamp']
# character_count = json_values['character_count']

# print(f'Input is: {rq_input}')
# print(f'Date is: {datetime.fromtimestamp(timestamp)}')
# print(f'character_count is: {character_count}')



#defien variables
#  API_TOKEN = '5767083831:AAHjXCOMr8Akl-k8tpPJB6YfC1Zn775InWo' #nawzaysfinah_bot
API_TOKEN = '5912247638:AAHo1kYgW2c6TWiOuJAlWuSfKouzoVAFTQE'
NOTION_TOKEN = "secret_aMGOZvx3omcSowLfmIOi93VeQBWU5LVWDXknwtXrXBy"
DATABASE_ID = "a0238c1d750f447da33929fedff8b494"

# Create an Updater instance using the telegram API token
updater = Updater(token=API_TOKEN, use_context=True)
dispatcher = updater.dispatcher

headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

updater.start_polling()

# Define a handler functions
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! Welcome to the Gimme Quotes Bot!\nDo you have quotes for me?\n\n"
    + "Please send them to me in the following format:\n'This is the quote.'/'This is the author's name'\n\n"
    + "e.g. I am tired of programming/Syaz\n\n"
    + "If you're ready, just type /quote_bot")

# Add the handler functions to the dispatcher
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

    
def quote_bot(update, context):
# Collect the message
    message = update.message.text
    print(message)

    if message == "/quote_bot":
        print("dont print anything")
        context.bot.send_message(chat_id=update.effective_chat.id, text="what new quote do you have for me today?\n")
    else:
        def create_page(data: dict):
                create_url = "https://api.notion.com/v1/pages"
                
                payload = {"parent": {"database_id" : DATABASE_ID}, "properties": data}

                res = requests.post(create_url, headers=headers, json=payload)
                apple = str(res.status_code)
                print(apple)
                # if apple == 200:
                #     print("cool that worked! Thanks for that")
                # else:
                #     print("that didn't work, are you sure you followed the format correctly?")
                return res

        quote_in, author_in = message.split("/")
        print(quote_in)
        print(author_in)

        Author =  author_in
        Quote = quote_in

        context.bot.send_message(chat_id=update.effective_chat.id, text='"'+ Quote + '"\n' + Author + '\n\nThank you for the quote!')
        published_date = datetime.now().astimezone(timezone.utc).isoformat()
        data = {
            "Author": {"title": [{"text": {"content": Author}}]},
            "Quote": {"rich_text": [{"text": {"content": Quote}}]},
            "Published": {"date": {"start": published_date, "end": None}}
        }
        create_page(data)

    # Start the polling loop to listen for incoming messages
updater.start_polling()

message_handler = MessageHandler(Filters.text, quote_bot)
dispatcher.add_handler(message_handler)

quote_bot_handler = CommandHandler('quote_bot', quote_bot)
dispatcher.add_handler(quote_bot_handler)

    


# def get_pages(num_pages=None):
#     url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

#     get_all = num_pages is None
#     page_size = 100 if get_all else num_pages
#     payload = {"page_size": page_size}

#     response = requests.post(url, json=payload, headers=headers)
    
#     data = response.json()
    

#     # Comment this out to dump all data to a file
#     import json
#     with open('db.json', 'w', encoding='utf8') as f:
#        json.dump(data, f, ensure_ascii=False, indent=4)

#     results = data["results"]
#     # while data["has_more"] and get_all:
#     #     payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
#     #     url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
#     #     response = requests.post(url, json=payload, headers=headers)
#     #     data = response.json()
#     #     results.extend(data["results"])

#     return results

# pages = get_pages()

# for page in pages:
#     page_id = page["id"]
#     props = page["properties"]
#     url = props["URL"]["title"][0]["text"]["content"]
#     title = props["Title"]["rich_text"][0]["text"]["content"]
#     published = props["Published"]["date"]["start"]
#     published = datetime.fromisoformat(published)

# print(url, title, published)




