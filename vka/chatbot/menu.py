# -*- coding: utf-8 -*-
from vka import Keyboard, Button

# TODO Переписать чтобы работало


def any_button(): ...
def back_button(): ...


class CreatorMenu:
    def __init__(self, menu_commands: list, command: str, func_obj):
        self.command = command
        self.func_obj = func_obj
        self.__menu_commands__ = menu_commands
        self.__menu_commands__.append({'command': command, 'func_obj': func_obj, 'button': []})
        self.index = [
            self.__menu_commands__.index(i) for i in self.__menu_commands__
            if i['command'] == self.command
        ][0]
        self.__menu_commands__[self.index]['menu'] = []

    def add_menu(
            self, command: str, icon: str,
            category: str = None, subcategory: str = None,
    ):
        self.__menu_commands__[self.index]['menu'].append(
            {
                'command': command,
                'category': category,
                'subcategory': subcategory,
                'icon': icon,
                'button': [],
            }
        )

    def keyboard_generation(
        self
    ):
        for i in self.__menu_commands__:
            if i['button']:
                keyboard = Keyboard(
                    inline=True
                )
                for j in self.__menu_commands__[self.index]['menu']:
                    if j['category'] is not None and \
                            j['category'] is None:
                        keyboard.add(
                            Button.callback(j['icon']).secondary().on_called(
                                self.func_obj, args=j['category']
                            ),
                        )
                if len(keyboard.scheme["buttons"]) == 3:
                    keyboard.new_line()

        for i in self.__menu_commands__[self.index]['menu']:
            if not i['button']:
                keyboard = Keyboard(
                    inline=True
                )
                for j in self.__menu_commands__[self.index]['menu']:
                    if i['category'] == j['subcategory'] and \
                            j['category'] is not None \
                            and i['category'] is not None:
                        keyboard.add(
                            Button.callback(j['icon']).secondary().on_called(
                                self.func_obj, args=j['category']
                            ),
                        )
                if len(keyboard.scheme["buttons"]) == 3:
                    keyboard.new_line()
                if keyboard.scheme["buttons"] != [[]]:
                    keyboard.add(
                        Button.callback('⬅️').secondary().on_called(
                            back_button, args=i['category']
                        ),
                    )
                i['button'] = keyboard if keyboard.scheme["buttons"] != [[]] else []


# m = CreatorMenu([], 'магазин', func_obj=any_button)
# m.add_menu(command='товары', category='store', icon='🧳')
# m.add_menu(command='история покупок', category='history_buy', icon='🛍')
# m.add_menu(command='активные покупки', category='active_buy', icon='🛒')
# m.add_menu(command='вип', category='vip', icon='💎', subcategory='store')
# m.add_menu(command='аренда', category='rent', icon='📃', subcategory='store')
# m.add_menu(
#     command='1 день - 1р\n7 дней - 10р\n30 дней - 50р',
#     icon='', subcategory='vip'
# )
# m.add_menu(
#     command='30 дней - 100р',
#     icon='', subcategory='rent'
# )
#
# m.keyboard_generation()

