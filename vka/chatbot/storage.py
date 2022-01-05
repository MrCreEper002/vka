
class KeyAndBoxStorage:
    """
    KeyAndBoxStorage - это хранилище ключей и хранилище добавленных команд в бота для
    быстрого сохранения и использования их процессе работы
    """
    __state__: dict = {}

    __commands__: list = []
    __addition__: dict = {}
    __callback_action__: dict = {}

    def __setitem__(self, key, value):
        self.__state__[key] = value

    def __getitem__(self, key):
        return self.__state__[key]

    def __delitem__(self, key):
        del self.__state__[key]
