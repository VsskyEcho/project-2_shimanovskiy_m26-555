import shlex

import prompt
from prettytable import PrettyTable

from primitive_db import core
from primitive_db.constants import ID_COLUMN, META_FILE
from primitive_db.decorators import handle_db_errors
from primitive_db.parser import parse_condition, parse_values
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_bad_value(value):
    """Пишет что пользователь ввёл что-то не то."""
    print(f"Некорректное значение: {value}. Попробуйте снова.")


def print_records(table_columns, records):
    """Выводит записи табличкой через prettytable."""
    table = PrettyTable()
    table.field_names = list(table_columns)
    for record in records:
        table.add_row([record[column] for column in table_columns])
    print(table)


@handle_db_errors
def find_ids(table_name, table_data, where_clause):
    """Возвращает ID записей под условие where или None, если таких нет."""
    found = core.find_records(table_data, where_clause)
    if not found:
        print(f'В таблице "{table_name}" нет записей по такому условию.')
        return None
    return [record[ID_COLUMN] for record in found]


def run_create_table(metadata, args):
    """create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ..."""
    # нужно имя таблицы и хотя бы один столбец
    if len(args) < 3:
        raise ValueError(" ".join(args))

    new_metadata = core.create_table(metadata, args[1], args[2:])
    if new_metadata is not None:
        save_metadata(META_FILE, new_metadata)


def run_drop_table(metadata, args):
    """drop_table <имя_таблицы>"""
    if len(args) != 2:
        raise ValueError(" ".join(args))

    table_name = args[1]
    # проверяем заранее, чтобы не спрашивать "вы уверены?" про несуществующую
    if not core.check_table_exists(metadata, table_name):
        return

    new_metadata = core.drop_table(metadata, table_name)
    if new_metadata is not None:
        save_metadata(META_FILE, new_metadata)
        # вместе с таблицей удаляем и её данные, иначе при создании таблицы
        # с тем же именем вылезут старые записи
        delete_table_data(table_name)


def run_insert(metadata, args):
    """insert into <имя_таблицы> values (<значение1>, <значение2>, ...)"""
    if len(args) < 5 or args[1] != "into" or args[3] != "values":
        raise ValueError(" ".join(args))

    table_name = args[2]
    values = parse_values(" ".join(args[4:]))

    table_data = core.insert(metadata, table_name, values)
    if table_data is not None:
        save_table_data(table_name, table_data)


def run_select(metadata, args):
    """select from <имя_таблицы> [where <столбец> = <значение>]"""
    if len(args) < 3 or args[1] != "from":
        raise ValueError(" ".join(args))

    table_name = args[2]
    where_clause = None
    if len(args) > 3:
        if args[3] != "where":
            raise ValueError(" ".join(args))
        where_clause = parse_condition(" ".join(args[4:]))

    if not core.check_table_exists(metadata, table_name):
        return
    table_data = load_table_data(table_name)

    records = core.select(table_data, where_clause)
    if records is not None:
        print_records(metadata[table_name], records)


def run_update(metadata, args):
    """update <имя_таблицы> set <столбец> = <значение> where <столбец> = <значение>"""
    if len(args) < 4 or args[2] != "set" or "where" not in args:
        raise ValueError(" ".join(args))

    table_name = args[1]
    where_index = args.index("where")
    set_clause = parse_condition(" ".join(args[3:where_index]))
    where_clause = parse_condition(" ".join(args[where_index + 1:]))

    if not core.check_table_exists(metadata, table_name):
        return
    table_data = load_table_data(table_name)

    # запоминаем ID заранее, чтобы потом написать какие записи поменялись
    ids = find_ids(table_name, table_data, where_clause)
    if ids is None:
        return

    new_data = core.update(table_data, set_clause, where_clause)
    if new_data is not None:
        save_table_data(table_name, new_data)
        for record_id in ids:
            print(
                f'Запись с ID={record_id} в таблице "{table_name}" успешно обновлена.'
            )


def run_delete(metadata, args):
    """delete from <имя_таблицы> where <столбец> = <значение>"""
    if len(args) < 5 or args[1] != "from" or args[3] != "where":
        raise ValueError(" ".join(args))

    table_name = args[2]
    where_clause = parse_condition(" ".join(args[4:]))

    if not core.check_table_exists(metadata, table_name):
        return
    table_data = load_table_data(table_name)

    ids = find_ids(table_name, table_data, where_clause)
    if ids is None:
        return

    new_data = core.delete(table_data, where_clause)
    if new_data is not None:
        save_table_data(table_name, new_data)
        for record_id in ids:
            print(f'Запись с ID={record_id} успешно удалена из таблицы "{table_name}".')


def run_info(metadata, args):
    """info <имя_таблицы>"""
    if len(args) != 2:
        raise ValueError(" ".join(args))

    table_name = args[1]
    if not core.check_table_exists(metadata, table_name):
        return
    table_data = load_table_data(table_name)

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {core.columns_to_text(metadata[table_name])}")
    print(f"Количество записей: {len(table_data)}")


def run():
    """Главный цикл программы: читает команды и вызывает нужные функции."""
    print_help()

    while True:
        # каждый раз берём свежие метаданные из файла
        metadata = load_metadata(META_FILE)

        user_input = prompt.string(">>>Введите команду: ")

        # shlex сам разбивает строку по пробелам и понимает кавычки.
        # posix=False - чтобы кавычки НЕ удалялись: по ним парсер отличает
        # строку "28" от числа 28
        try:
            args = shlex.split(user_input, posix=False)
        except ValueError:
            # например, если не закрыли кавычку
            print_bad_value(user_input)
            continue

        # ввели одни пробелы
        if not args:
            continue

        command = args[0]

        # все run_... кидают ValueError, если команда или значение кривые
        try:
            match command:
                case "create_table":
                    run_create_table(metadata, args)
                case "drop_table":
                    run_drop_table(metadata, args)
                case "list_tables":
                    core.list_tables(metadata)
                case "insert":
                    run_insert(metadata, args)
                case "select":
                    run_select(metadata, args)
                case "update":
                    run_update(metadata, args)
                case "delete":
                    run_delete(metadata, args)
                case "info":
                    run_info(metadata, args)
                case "help":
                    print_help()
                case "exit":
                    break
                case _:
                    print(f"Функции {command} нет. Попробуйте снова.")
        except ValueError as error:
            # в ошибке лежит неправильная часть команды (если пусто - вся команда)
            print_bad_value(str(error) or user_input)
