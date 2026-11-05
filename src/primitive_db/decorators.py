import time

import prompt


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


def confirm_action(action_name):
    """Фабрика декораторов: спрашивает подтверждение перед опасной операцией.

    Если ответили не "y" - операция отменяется и функция не вызывается.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            question = f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            # empty=True - чтобы просто Enter тоже считался отказом
            answer = prompt.string(question, empty=True)
            if answer != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Декоратор: замеряет, сколько выполнялась функция, и печатает время."""

    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        print(f"Функция {func.__name__} выполнилась за {end - start:.3f} секунд.")
        return result

    return wrapper
