import prompt


def print_help():
    """Выводит список доступных команд."""
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")


def welcome():
    """Приветствует пользователя и крутит простой цикл команд."""
    print("Первая попытка запустить проект!")
    print("***")
    print_help()

    # спрашиваем команды пока не введут exit
    while True:
        command = prompt.string("Введите команду: ")
        if command == "exit":
            break
        elif command == "help":
            print_help()
