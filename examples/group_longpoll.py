# -*- coding: utf-8 -*-
from vka import ABot, Context, Keyboard, Button


bot = ABot(token='group_token')
# используется для хранения и быстрого доступа в командах
# так же можно записать объекты функций
bot.set_item(key='admin', value=1)


@bot.add_command(commands='привет')
async def greet(ctx: Context):
    # для вызова записанной переменной
    admin = ctx.bot.get_item(key='admin')
    user = await ctx.user_get(user_ids=admin)
    await ctx.answer(f'ПРИВЕТ, мой админ {user:@full_name}')


@bot.add_command(commands='кто ты')
async def me(ctx: Context):
    # получение информации о пользователе который только что написал
    user = ctx.fetch_sender()
    # быстрое форматирование в строку
    # f"{user:id}" - только айди
    # f"{user:fn}" - только имя
    # f"{user:ln}" - только фамилию
    # f"{user:full_name}" - имя и фамилию
    # f"{user:@fn}" - сделать имя кликабельное. работает со всеми выше перечисленными
    await ctx.reply(f'{user:@full_name}, я бот.')


@bot.add_command(commands='команды')
async def greet(ctx: Context):
    # клавиатура будет как обычная не прилепленная к сообщению
    keyboard = Keyboard(
        Button.text('Первая команда').positive(),
        Button.text('Вторая команда').negative(),
        Button.text('Третья команда').primary(),
        Button.text('Четвертая команда').secondary(),
        ...,  # чтобы перенести клавиатуру на новую строчку
        Button.text('Пятая команда').secondary(),
    )
    # чтобы добавить в последнюю строчку еще кнопку
    keyboard.add(
        Button.open_link('Профиль', 'https://vk.com/id1'),
    )
    # чтобы добавить клавиатуру с новой строчки
    keyboard.new_line()
    keyboard.add(
        Button.text('Седьмая кнопка',).secondary(),
    )
    await ctx.answer('команды', keyboard=keyboard)


def cancel(): ...


@bot.add_command(commands='поиск')
async def greet(ctx: Context):
    # чтобы получать в этой команде дальше новые сообщение для других данных
    # если указать параметр `any_user=True` то будет получать сообщение от всех пользователей
    async for new_ctx in ctx.receive_new_message():
        # если нужно завершить по нажатию кнопки
        if new_ctx.button_checking(cancel, ctx.msg.from_id):
            break


# регистрация callback кнопок
@bot.add_click_callback(show_snackbar=True)
async def show_snackbar():
    return 'Произошло чудо 🧩'


@bot.add_click_callback(callback=True)
async def callback(ctx: Context, argument=None):
    if not isinstance(argument, dict):
        return
    # чтобы отредактировать последние сообщение бота
    await ctx.transmit(
        f'Сработал callback кнопка '
        f'после команды - {argument["text"]}!'
    )


@bot.add_command(commands='меню')
async def greet(ctx: Context):
    # клавиатура будет прилепленная к сообщению
    keyboard = Keyboard(
        Button.callback('Первая команда').positive().on_called(
            greet
        ),
        Button.callback('Вторая команда').negative().on_called(
            callback, text=ctx.msg.text
        ),
        inline=True
    )

    await ctx.answer('меню', keyboard=keyboard)


bot.run()
