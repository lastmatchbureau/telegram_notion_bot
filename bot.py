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
    print(message.chat.id)


@bot.message_handler(commands=["test"])
def next_command(message):
    nh = NotionHandler()
    tasks = nh.get_tasks()
    task = tasks[0]
    bot.send_message(message.chat.id, nh.get_msg(task))
    print(message.chat.id)


bot.polling()
