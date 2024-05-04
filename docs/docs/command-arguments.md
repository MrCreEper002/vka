# Создание команд с аргументами и без аргументов

***

## Команда без аргумента

```python
import re
from vka import ABot, Context

bot = ABot(token='group_token')


@bot.add_command(commands='пока')
async def greet(ctx: Context):
    # получить информацию том о пользователе который написал команду
    from_id = await ctx.fetch_sender()
    
    await ctx.answer(f'{from_id:@fn}, до встречи.')

bot.run()
```

## Команда с аргументом

!!! note
    Если команда пишется с аргументом то нужно обязательно указать переменную в функции иначе функция не сработает 

```python
import re
from vka import ABot, Context

bot = ABot(token='group_token')


def get_id(com_name: str) -> str:
    if com_name.find('vk.com/') != -1:
        return com_name[com_name.find('vk.com/') + 7::]
    elif com_name.find('https://vk.com/') != -1:
        return com_name[com_name.find('https://vk.com/') + 7::]
    return re.search(r'[a-zA-Z0-9_.]+|[\^]]+]', com_name).group()


@bot.add_command(commands='привет')
async def greet(ctx: Context, argument=None):
    # получить информацию том о пользователе который написал команду
    from_id = await ctx.fetch_sender()
    # получить информацию о пользователе который в аргументе
    user = await ctx.user_get(user_ids=get_id(argument))
    await ctx.answer(f'{user:@full}, передает привет {from_id:@fn}')

bot.run()

```






