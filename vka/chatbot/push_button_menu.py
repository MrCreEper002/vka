# -*- coding: utf-8 -*-
from typing import Callable

from vka.base.exception import VkaError


class CreatorButtonCommands:
    """
    commands_button = {
        'menu': {
            'commands': [],  # команды от которых будет вызываться данная функция
            'text': ['...', ...],  # текст который будет выдаваться при написании команды или нажатие на кнопку
            'button': ['commands', ...],  # какие кнопки будут прикреплены кнопки к этому сообщению
            'attachment': ['', ...],  # вложение какие могут прикрепляться
            'function': ...,  # функция которая будет запускаться
        },
        'commands': {
            'text': '...',
        }
    }
    """

    def __init__(self):
        self.commands_button = {}

    def add(
            self, name_button: str, function: Callable,
            text: list[str], commands: list[str] = None,
            button: list[str] = None, attachment: list[str] = None,
    ):
        if self.commands_button.get(name_button):
            raise VkaError('Данная переменная уже добавлена.')

        self.commands_button[name_button] = {
            'function': function,
            'commands': commands,
            'text': text,
            'button': button,
            'attachment': attachment,
        }


def menu_button(): ...


creator_menu = CreatorButtonCommands()

creator_menu.add(name_button='menu', function=menu_button, text=['MENU'], button=['commands'])
creator_menu.add(name_button='commands', function=menu_button, text=['Commands'])

print(creator_menu.commands_button)
