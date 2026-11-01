import json
import os

from primitive_db.constants import DATA_DIR


def load_metadata(filepath):
    """Загружает метаданные из JSON-файла. Если файла нет - возвращает {}."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        # первый запуск, файла ещё нет - значит и таблиц нет
        return {}


def save_metadata(filepath, data):
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_table_filepath(table_name):
    """Возвращает путь к файлу с данными таблицы, например data/users.json."""
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name):
    """Загружает записи таблицы. Если файла нет - возвращает пустой список."""
    try:
        with open(get_table_filepath(table_name), "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        # в таблицу ещё ничего не добавляли
        return []


def save_table_data(table_name, data):
    """Сохраняет записи таблицы в её JSON-файл."""
    # папки data может ещё не быть
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(get_table_filepath(table_name), "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def delete_table_data(table_name):
    """Удаляет файл с данными таблицы (нужно при drop_table)."""
    filepath = get_table_filepath(table_name)
    if os.path.exists(filepath):
        os.remove(filepath)
