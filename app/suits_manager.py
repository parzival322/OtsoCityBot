import os
import json
from PIL import Image
from pathlib import Path


DATA_DIR = os.getenv('DATA_DIR', os.path.join(os.path.dirname(__file__),  'data') )

PERMISSIONS_FILE = os.getenv('PERMISSIONS_FILE', os.path.join(os.path.dirname(__file__), 'data/permissions.json') )

TEMP_DIR = os.getenv('TEMP_DIR', os.path.join(os.path.dirname(__file__),  'data/temp') )

RESULTS_DIR = os.getenv('RESULTS_DIR', os.path.join(os.path.dirname(__file__),  'data/results') )


#================СПИСОК ФОРМ================
def get_all_suits() -> list:
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    suits = []
    print(f"Ищем файлы в: {os.path.abspath(DATA_DIR)}")

    for file in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, file)

        if os.path.isdir(file_path):
            continue

        filename, ext = os.path.splitext(file)

        ext = ext.lstrip('.')

        if ext.lower() == 'png':
            try:
                with Image.open(file_path) as img:
                    w, h = img.size

                    if w == 64 and h == 64:
                        suits.append(filename)

            except Exception as e:
                print(f'Ошибка при чтении файла {file}: {e}')

    return suits


#================УСТАНОВКА И ПРОВЕРКА ДОСТУПА================
def set_access(user_id: int, suit_name: str, allow: bool = True):
    if os.path.exists(PERMISSIONS_FILE):
        with open(PERMISSIONS_FILE, mode='r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f'Ошибка при чтении доступов: {e}')
                return ["ERROR", 1]
    else:
        data = {}

    user_key = str(user_id)

    if user_key not in data:
        data[user_key] = []

    if suit_name not in data[user_key] and allow:
        data[user_key].append(suit_name)
    if suit_name in data[user_key] and not allow:
        data[user_key].remove(suit_name)

    file_dir = os.path.dirname(PERMISSIONS_FILE)
    if file_dir:
        os.makedirs(file_dir, exist_ok=True)

    with open(PERMISSIONS_FILE, mode='w', encoding='utf-8') as f:
        try:
            json.dump(data, f, ensure_ascii=False, indent=4)
            return ["OK", 0]
        except Exception as e:
            print(f'Ошибка при установке доступов: {e}')
            return ["ERROR", 2]


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


#================ОБРАБОТКА СКИНА================
def blend_skin_with_suit(skin_path: str, suit_path: str, output_path: str) -> str:
    skin = Image.open(skin_path).convert("RGBA")
    suit = Image.open(suit_path).convert("RGBA")

    try:
        result = Image.alpha_composite(skin, suit)

        path_obj = Path(output_path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Сохраняем, используя путь
        result.save(path_obj, "PNG")

        print(f'Успешное смешивание {skin_path} и {suit_path}')

        return 'OK'
    except Exception as e:
        print(f'Возникла ошибка при смешивании {skin_path} и {suit_path} : \n {e}')
        return 'ERROR'
