def handle_db_errors(func):
    """Декоратор: ловит типичные ошибки работы с БД и печатает сообщение.

    Так не надо писать try...except в каждой функции.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            # формат как в задании для некорректных значений
            print(f"Некорректное значение: {e}. Попробуйте снова.")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
        # если была ошибка - функция вернёт None

    return wrapper
