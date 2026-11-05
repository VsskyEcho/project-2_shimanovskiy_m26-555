from primitive_db.constants import ID_COLUMN, ID_TYPE, VALID_TYPES
from primitive_db.decorators import confirm_action, handle_db_errors, log_time
from primitive_db.utils import load_table_data


def columns_to_text(table_columns):
    """Делает из словаря столбцов строку вида "ID:int, name:str"."""
    parts = []
    for column_name, column_type in table_columns.items():
        parts.append(f"{column_name}:{column_type}")
    return ", ".join(parts)


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу и возвращает обновлённые метаданные.

    columns - список строк вида "name:str". Столбец ID:int добавляется сам.
    Если что-то не так - пишет ошибку и возвращает None.
    """
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None

    # ID всегда идёт первым столбцом
    table_columns = {ID_COLUMN: ID_TYPE}

    for column in columns:
        # "name:str" -> "name" и "str" (если двоеточия нет, тип будет пустой)
        column_name, _, column_type = column.partition(":")

        # ID мы и так добавили сами, второй раз не нужен
        if column_name == ID_COLUMN:
            continue

        # имя не пустое и не повторяется, а тип только из разрешённых
        is_bad_name = column_name == "" or column_name in table_columns
        if is_bad_name or column_type not in VALID_TYPES:
            raise ValueError(column)

        table_columns[column_name] = column_type

    metadata[table_name] = table_columns

    columns_text = columns_to_text(table_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_text}')
    return metadata


def check_table_exists(metadata, table_name):
    """Проверяет, что таблица есть. Если нет - пишет ошибку и возвращает False."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    return True


@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных и возвращает их (или None если таблицы нет)."""
    if not check_table_exists(metadata, table_name):
        return None

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Печатает список всех таблиц."""
    if not metadata:
        print("Таблиц пока нет.")
        return

    for table_name in metadata:
        print(f"- {table_name}")


# log_time должен быть ближе к функции, иначе он напечатает имя wrapper
@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Добавляет новую запись в таблицу и возвращает все данные таблицы.

    values - значения всех столбцов кроме ID (ID генерируется сам).
    """
    if not check_table_exists(metadata, table_name):
        return None

    table_columns = metadata[table_name]

    # все столбцы кроме ID - их пользователь и передаёт
    user_columns = []
    for column_name in table_columns:
        if column_name != ID_COLUMN:
            user_columns.append(column_name)

    if len(values) != len(user_columns):
        raise ValueError(
            f"количество значений {len(values)}, а нужно {len(user_columns)}"
        )

    table_data = load_table_data(table_name)

    # новый ID = самый большой ID + 1 (или 1, если записей ещё нет)
    ids = [record[ID_COLUMN] for record in table_data]
    if ids:
        new_id = max(ids) + 1
    else:
        new_id = 1

    # ID идёт первым, дальше остальные столбцы, заодно проверяем типы
    new_record = {ID_COLUMN: new_id}
    for column_name, value in zip(user_columns, values):
        column_type = table_columns[column_name]
        # type() а не isinstance(), потому что True это тоже int в питоне
        if type(value) is not VALID_TYPES[column_type]:
            raise ValueError(value)
        new_record[column_name] = value

    table_data.append(new_record)

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


def is_match(record, where_clause):
    """Проверяет, подходит ли запись под условие where (например {'age': 28})."""
    for column, value in where_clause.items():
        # если такого столбца нет, тут будет KeyError
        if record[column] != value:
            return False
    return True


def find_records(table_data, where_clause):
    """Возвращает список записей, подходящих под условие where.

    Если столбца нет - вылетит KeyError, его ловит декоратор у того,
    кто эту функцию вызвал.
    """
    found = []
    for record in table_data:
        if is_match(record, where_clause):
            found.append(record)
    return found


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает все записи или только те, что подходят под where."""
    if where_clause is None:
        return table_data
    return find_records(table_data, where_clause)


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Меняет поля из set_clause у записей, подходящих под where. Возвращает данные."""
    for record in find_records(table_data, where_clause):
        for column, new_value in set_clause.items():
            if column not in record:
                raise KeyError(column)
            # ID менять нельзя, иначе могут появиться одинаковые ID
            if column == ID_COLUMN:
                raise ValueError(column)
            # тип нового значения должен совпадать с типом столбца
            if type(new_value) is not type(record[column]):
                raise ValueError(new_value)
            record[column] = new_value

    return table_data


# сначала спрашиваем подтверждение, потом уже выполняем с обработкой ошибок
@confirm_action("удаление записи")
@handle_db_errors
def delete(table_data, where_clause):
    """Удаляет записи, подходящие под where. Возвращает оставшиеся данные."""
    new_data = []
    for record in table_data:
        if not is_match(record, where_clause):
            new_data.append(record)
    return new_data
