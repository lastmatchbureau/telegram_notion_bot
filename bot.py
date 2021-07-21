import telebot
from notion_module import NotionHandler
from dotenv import load_dotenv
from os import environ
from fix_links import fix_links

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
        try:
            task = fix_links(task)
            bot.send_message(message.chat.id, task, parse_mode="html", disable_web_page_preview=True)
        except Exception as e:
            print(e.args)
            print(task)
            print(len(task))


bot.polling()
