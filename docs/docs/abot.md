# ABot

Создание бота во ВКонтакте.

!!! Tip
    Параметры такие же, как в **[API](https://vka.readthedocs.io/ru/latest/docs/api/)**


## Инициализация бота

```python
from vka import ABot

bot = ABot(token='token')
```
## Добавление команд
* `@bot.add_command(commands=('start'))` - через вызов декоратор
* `bot.register_command(func=Callable[[Context], Any], commands=('start'))` - через вызов метода

## Запуск бота
#### Первый способ
```python
from vka import ABot

bot = ABot(token='token')

bot.run()
```

#### Второй способ
```python
from vka import ABot
import asyncio

async def main():
    bot = ABot(token='token')
    
    await bot.async_run()

asyncio.run(main())
```