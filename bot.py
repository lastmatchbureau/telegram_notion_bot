import os

import telebot
from notion_module import NotionHandler
from dotenv import load_dotenv
from os import environ

load_dotenv('.env')
token = environ["API_KEY"]

bot = telebot.TeleBot(token)


@bot.message_handler(commands=["start"])
def start_command(message):
    bot.send_message(message.chat.id, "Send /test to get started")


@bot.message_handler(commands=["test"])
def next_command(message):
    nh = NotionHandler()
    tasks = nh.get_task()
    for task in tasks:
        files_to_upload = nh.downloaded_files
        bot.send_message(message.chat.id, task, parse_mode="MarkdownV2", disable_web_page_preview=True)
        if files_to_upload:
            for file in files_to_upload:
                bot.send_document(message.chat.id, open(file, 'rb'))
                os.remove(file)


bot.polling()
