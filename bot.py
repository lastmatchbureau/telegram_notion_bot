import telebot
from telebot.types import Message
from notion_handler import NotionHandler, SearchProperties
from dotenv import load_dotenv
from os import environ
from upload_func import upload_file
from buttons import start_search_reply_buttons, continue_search_reply_buttons

load_dotenv('.env')
token = environ["API_KEY"]
search_requests = {}
bot = telebot.TeleBot(token)


def get_search_property(message):
    sp = SearchProperties()
    if "/search_name " in message.text:
        sp.__setattr__("name", message.text.replace("/search_name ", ""))
    if "/search_type " in message.text:
        sp.__setattr__("t_type", message.text.replace("/search_type ", ""))
    if "/search_status " in message.text:
        sp.__setattr__("status", message.text.replace("/search_status ", ""))
    return sp


def delete_prefix(message: Message):
    if "/search_name " in message.text:
        message.text = message.text.replace("/search_name ", "")
    if "/search_type " in message.text:
        message.text = message.text.replace("/search_type ", "")
    if "/search_status " in message.text:
        message.text = message.text.replace("/search_type ", "")
    return message


@bot.message_handler(commands=["start"])
def start_command(message):
    bot.send_message(message.chat.id, "Send /test to get started")


@bot.message_handler(commands=["test"])
def next_command(message):
    print(message.text)
    nh = NotionHandler(tg_id=message.chat.id)
    sp = SearchProperties()
    tasks = nh.find_tasks(search_prop=sp)
    bot.send_message(message.chat.id,
                     "Результатов по данному запросу может быть очень много, поэтому используйте кнопки "
                     "под этим сообщением, чтобы управлять поисковой выдачей",
                     reply_markup=start_search_reply_buttons)
    search_requests.update({message.chat.id: tasks})


@bot.message_handler(commands=['search_name', 'search_type', 'search_status'])
def search_name_command(message):
    print(message.text)
    nh = NotionHandler(tg_id=message.chat.id)
    sp = get_search_property(message)
    tasks = nh.find_tasks(search_prop=sp)
    bot.send_message(message.chat.id,
                     "Результатов по данному запросу может быть очень много, поэтому используйте кнопки "
                     "под этим сообщением, чтобы управлять поисковой выдачей",
                     reply_markup=start_search_reply_buttons)
    search_requests.update({message.chat.id: tasks})


@bot.callback_query_handler(func=lambda x: True)
def callback_query_handler(call):
    bot.send_chat_action(call.message.chat.id, "typing")
    search_request_id = call.message.chat.id
    nh = NotionHandler(tg_id=call.message.chat.id)
    try:
        tasks = search_requests[search_request_id]
    except KeyError:
        bot.send_message(call.message.chat.id, "Поисковой запрос не найден, составьте новый поисковой запрос!")
        return None
    if "next" in call.data:
        how_much_tasks = int(call.data.replace("next", ""))
        for i in range(how_much_tasks):
            try:
                task = next(tasks)
            except StopIteration:
                task = "Конец поисковой выдачи"
                bot.send_message(call.message.chat.id, task, parse_mode="MarkdownV2", disable_web_page_preview=True)
                bot.send_message(call.message.chat.id, "Поиск завершен")
                return None
            files_to_upload = nh.downloaded_files
            bot.send_message(call.message.chat.id, task, parse_mode="MarkdownV2", disable_web_page_preview=True)
            if files_to_upload:
                for file in files_to_upload:
                    upload_file(call.message.chat.id, file, token)

        bot.send_message(call.message.chat.id, "Меню поиска:", reply_markup=continue_search_reply_buttons)
    if "stop" in call.data:
        search_requests.pop(search_request_id)
        nh.delete_files()
        bot.send_message(call.message.chat.id, "Поиск завершен")


while True:
    try:
        nh = NotionHandler()
        task = nh.new_task_available()
        if task:
            bot.send_chat_action(231584958, "typing", timeout=10)
            new_task_txt = nh.get_new_task(task)
            bot.send_message(231584958, new_task_txt, parse_mode="MarkdownV2")
        bot.polling()
    except Exception as e:
        bot.send_message(231584958, e)
