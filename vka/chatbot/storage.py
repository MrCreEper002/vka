
class KeyAndBoxStorage:
    """
    KeyAndBoxStorage - это хранилище ключей и хранилище добавленных команд в бота для
    быстрого сохранения и использования их процессе работы
    """

    def __init__(self):
        self.__state__: dict = {}
        self.__message_ids__: dict = {}
        self.__commands__: list = []
        self.__menu_commands__: list = []
        self.__addition__: dict = {}
        self.__callback_action__: dict = {}

    def set_item(self, key, value):
        self.__state__[key] = value

    def get_item(self, key):
        return self.__state__[key]

    def del_item(self, item):
        del self.__state__[item]



