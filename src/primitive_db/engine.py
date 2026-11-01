import shlex

import prompt

from primitive_db import core
from primitive_db.constants import META_FILE
from primitive_db.utils import load_metadata, save_metadata


def print_help():
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_bad_value(value):
    """Пишет что пользователь ввёл что-то не то."""
    print(f"Некорректное значение: {value}. Попробуйте снова.")


def run():
    """Главный цикл программы: читает команды и вызывает нужные функции."""
    print_help()

    while True:
        # каждый раз берём свежие метаданные из файла
        metadata = load_metadata(META_FILE)

        user_input = prompt.string(">>>Введите команду: ")

        # shlex сам разбивает строку по пробелам и понимает кавычки
        try:
            args = shlex.split(user_input)
        except ValueError:
            # например, если не закрыли кавычку
            print_bad_value(user_input)
            continue

        # ввели одни пробелы
        if not args:
            continue

        command = args[0]

        match command:
            case "create_table":
                # нужно имя таблицы и хотя бы один столбец
                if len(args) < 3:
                    print_bad_value(user_input)
                    continue
                new_metadata = core.create_table(metadata, args[1], args[2:])
                if new_metadata is not None:
                    save_metadata(META_FILE, new_metadata)

            case "drop_table":
                if len(args) != 2:
                    print_bad_value(user_input)
                    continue
                new_metadata = core.drop_table(metadata, args[1])
                if new_metadata is not None:
                    save_metadata(META_FILE, new_metadata)

            case "list_tables":
                core.list_tables(metadata)

            case "help":
                print_help()

            case "exit":
                break

            case _:
                print(f"Функции {command} нет. Попробуйте снова.")
