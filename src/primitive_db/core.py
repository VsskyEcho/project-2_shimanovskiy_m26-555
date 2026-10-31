from primitive_db.constants import ID_COLUMN, ID_TYPE, VALID_TYPES


def columns_to_text(table_columns):
    """Делает из словаря столбцов строку вида "ID:int, name:str"."""
    parts = []
    for column_name, column_type in table_columns.items():
        parts.append(f"{column_name}:{column_type}")
    return ", ".join(parts)


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
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return None

        table_columns[column_name] = column_type

    metadata[table_name] = table_columns

    columns_text = columns_to_text(table_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_text}')
    return metadata


def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных и возвращает их (или None если таблицы нет)."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
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
