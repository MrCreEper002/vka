
class KeyAndBoxStorage:
    """
    KeyAndBoxStorage - это хранилище ключей и хранилище добавленных команд в бота для
    быстрого сохранения и использования их процессе работы
    """
    __state__: dict = {}

    __message_ids__: dict = {}

    __commands__: list = []
    __addition__: dict = {}
    __callback_action__: dict = {}

    def set_item(self, key, value):
        self.__state__[key] = value

    def get_item(self, key):
        return self.__state__[key]

    def del_item(self, item):
        del self.__state__[item]



