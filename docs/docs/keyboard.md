# Клавиатура

[Вся информация о клавиатуре есть в официальной документации ВК](https://dev.vk.com/ru/api/bots/development/keyboard)

***


### Какие бывают кнопки

 * __text()__: Кнопка типа `text`
 * __open_link()__: Кнопка типа `open_link`. Нельзя установить цвет для кнопки!
 * __location()__: Кнопка типа `location`. Нельзя установить цвет для кнопки!
 * __vk_pay()__: Кнопка типа `vk_pay`. Нельзя установить цвет для кнопки!
 * __open_app()__: Кнопка типа `open_app`. Нельзя установить цвет для кнопки!
 * __callback()__: Кнопка типа `callback`

### Цвета кнопок

 * __.positive()__: Зеленая кнопка (для обеих тем)
 * __.negative()__: Розовая (красная) кнопка (для обеих тем)
 * __.primary()__: Синяя кнопка для белой, белая для темной
 * __.secondary()__: Белая кнопка для светлой темы, серая для темной

***

## Создание обычной клавиатуры

```python
    @bot.add_command(commands='команды')
    async def commands(ctx: Context):
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
```

## Создание inline клавиатуры 

Все то же самое как обычное только добавляется параметр _inline=True_

```python
    @bot.add_command(commands='меню')
    async def commands(ctx: Context):
        keyboard = Keyboard(
            Button.text('Первая команда').positive(),
            inline=True
        )

        await ctx.answer('команды', keyboard=keyboard)
```



