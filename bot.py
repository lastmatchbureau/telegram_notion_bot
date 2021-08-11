import telebot
from telebot.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from notion_handler import NotionHandler, SearchProperties
from dotenv import load_dotenv
from os import environ
from upload_func import upload_file

load_dotenv('.env')
token = environ["API_KEY"]

bot = telebot.TeleBot(token)
reply_button = InlineKeyboardMarkup(row_width=1)
reply_button.add(InlineKeyboardButton("stop", callback_data="stop_search"))


def delete_prefix(message: Message):
    if "/search_name " in message.text:
        message.text = message.text.replace("/search_name ", "")
    if "/search_type " in message.text:
        message.text = message.text.replace("/search_type ", "")
    return message


@bot.message_handler(commands=["start"])
def start_command(message):
    bot.send_message(message.chat.id, "Send /test to get started")


@bot.message_handler(commands=["test"])
def next_command(message):
    print(message.chat.id)
    nh = NotionHandler()
    tasks = nh.get_task()
    for task in tasks:
        files_to_upload = nh.downloaded_files
        bot.send_message(message.chat.id, task, parse_mode="MarkdownV2", disable_web_page_preview=True)
        if files_to_upload:
            for file in files_to_upload:
                upload_file(message.chat.id, file, token)


@bot.message_handler(commands=['search_name'], func=delete_prefix)
def search_name_command(message):
    print(message.text)
    nh = NotionHandler()
    sp = SearchProperties(title=message.text)
    tasks = nh.find_tasks(search_prop=sp)
    for task in tasks:
        files_to_upload = nh.downloaded_files
        bot.send_message(message.chat.id, task, parse_mode="MarkdownV2", disable_web_page_preview=True)
        if files_to_upload:
            for file in files_to_upload:
                upload_file(message.chat.id, file, token)


@bot.message_handler(commands=['search_type'], func=delete_prefix)
def search_name_command(message):
    print(message.text)
    nh = NotionHandler()
    sp = SearchProperties(t_type=message.text)
    tasks = nh.find_tasks(search_prop=sp)
    for task in tasks:
        files_to_upload = nh.downloaded_files
        bot.send_message(message.chat.id, task, parse_mode="MarkdownV2", disable_web_page_preview=True,
                         reply_markup=reply_button)
        if files_to_upload:
            for file in files_to_upload:
                upload_file(message.chat.id, file, token)


@bot.callback_query_handler(func=lambda call: call=="stop_search")
def stop_search(call):
    pass


while True:
    try:
        bot.polling()
    except Exception as e:
        bot.send_message(231584958, str(e.args))
