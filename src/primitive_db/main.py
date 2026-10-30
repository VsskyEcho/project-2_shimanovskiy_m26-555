#!/usr/bin/env python3
from primitive_db.engine import welcome


def main():
    """Точка входа в программу."""
    welcome()


# main() вызываем только когда модуль запустили как программу,
# если его просто импортируют - ничего не печатаем
if __name__ == "__main__":
    main()
