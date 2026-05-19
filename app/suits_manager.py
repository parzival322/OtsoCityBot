import os
import json
from PIL import Image


DATA_DIR = '/app/data'
PERMISSIONS_FILE = '/app/data/permissions.json'


#================СПИСОК ФОРМ================
def get_all_suits() -> dict:
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    suits = {}

    for file in os.listdir(DATA_DIR):
        filename, ext = file.split('.')

        if ext.lower() == 'png':
            file_path = os.path.join(DATA_DIR, filename)
            try:
                with Image.open(file_path) as img:
                    w, h = img.size

                    if w == 64 and h == 64:
                        suits[filename] = file_path
            except Exception as e:
                print(f'Ошибка при чтении файлов: {e}')

    return suits


#================УСТАНОВКА И ПРОВЕРКА ДОСТУПА================
def set_access(user_id: int, suit_name: str, status: bool = True):
    if os.path.exists(PERMISSIONS_FILE):
        with open(PERMISSIONS_FILE, mode='r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                f.close()
            except Exception as e:
                print(f'Ошибка при чтении доступов: {e}')

        user_key = str(user_id)

        if user_key not in data:
            data[user_key] = []

        if suit_name and status not in data[user_key]:
            data[user_key].append(suit_name)
        if suit_name in data[user_key] and not status:
            data[user_key].remove(suit_name)

        with open(PERMISSIONS_FILE, mode='w', encoding='utf-8') as f:
            try:
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.close()
            except Exception as e:
                print(f'Ошибка при установке доступов: {e}')


def has_access(user_id: int, suit_name: str):
    if os.path.exists(PERMISSIONS_FILE):
        with open(PERMISSIONS_FILE, mode='r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                f.close()
            except Exception as e:
                print(f'Ошибка при проверке доступов: {e}')
        user_key = str(user_id)

        if user_key not in data:
            return False
        else:
            return suit_name in data[user_key]


#================ГРАФИЧЕСКАЯ ОБРАБОТКА================

