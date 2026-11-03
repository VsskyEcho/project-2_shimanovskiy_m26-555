from primitive_db.constants import QUOTES


def parse_value(text):
    """Превращает строку из команды в значение питона.

    "Sergei" (в кавычках) -> str, true/false -> bool, 28 -> int.
    Строки обязательно пишутся в кавычках, иначе это ошибка.
    """
    text = text.strip()

    # строка в кавычках - убираем кавычки
    if len(text) >= 2 and text[0] in QUOTES and text[-1] == text[0]:
        return text[1:-1]

    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False

    # остаётся только целое число, если не число - значит ввели что-то не то
    try:
        return int(text)
    except ValueError:
        raise ValueError(text)


def parse_condition(text):
    """Разбирает условие вида 'age = 28' в словарь {'age': 28}.

    Подходит и для where, и для set.
    """
    if "=" not in text:
        raise ValueError(text)

    # делим по первому "=", в самом значении (в кавычках) тоже может быть "="
    column, value = text.split("=", 1)
    column = column.strip()
    if column == "":
        raise ValueError(text)

    return {column: parse_value(value)}


def split_by_commas(text):
    """Делит строку по запятым, но запятые внутри кавычек не трогает."""
    parts = []
    current = ""
    quote = None  # какая кавычка сейчас открыта

    for char in text:
        if quote is None and char in QUOTES:
            quote = char
        elif char == quote:
            quote = None

        if char == "," and quote is None:
            parts.append(current)
            current = ""
        else:
            current += char

    parts.append(current)
    return parts


def parse_values(text):
    """Разбирает '("Sergei", 28, true)' в список ['Sergei', 28, True]."""
    text = text.strip()
    if not (text.startswith("(") and text.endswith(")")):
        raise ValueError(text)

    values = []
    for part in split_by_commas(text[1:-1]):
        # пустое значение, например "()" или "(1,,2)"
        if part.strip() == "":
            raise ValueError(text)
        values.append(parse_value(part))
    return values
