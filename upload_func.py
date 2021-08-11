import requests
from pathlib import Path
from os import remove


def upload_file(chat_id, file_path, api_token):
    file_size = (Path(file_path).stat().st_size / 1024) / 1024
    if file_size <= 50:
        print(f"sending {file_path} with size: {file_size} mb")
        url = f'https://api.telegram.org/bot{api_token}/sendDocument?chat_id={chat_id}'
        r = requests.post(url, files={"document": open(file_path, 'rb')})  # note: files, not data
        print(f"sent {file_path} with size: {file_size} mb")
    else:
        url = f'https://api.telegram.org/bot{api_token}/sendMessage'
        r = requests.post(url, json={"text": f"{file_path.replace('download/', '')} is bigger than 50 mb.", "chat_id": chat_id},)
    remove(file_path)