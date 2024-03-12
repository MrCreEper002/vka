# vka [![PyPI](https://img.shields.io/pypi/v/vka.svg)](https://pypi.org/project/vka/) ![Python 3.x](https://img.shields.io/pypi/pyversions/vka.svg)

![Static Badge](https://img.shields.io/badge/MrCreEper002-vka-vka)
![GitHub top language](https://img.shields.io/github/languages/top/MrCreEper002/vka)
![GitHub](https://img.shields.io/github/license/MrCreEper002/vka)
![GitHub Repo stars](https://img.shields.io/github/stars/MrCreEper002/vka)
![GitHub issues](https://img.shields.io/github/issues/MrCreEper002/vka)
[![Downloads](https://pepy.tech/badge/vka)](https://pepy.tech/project/vka)

#### Модуль сделана по основам [vk_api](https://github.com/python273/vk_api) и [vkquick](https://github.com/deknowny/vkquick)


[![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=pip+install+vka)](https://git.io/typing-svg)


### Полезная информация: 
* [Примеры](./examples)
* [Документация по методам API](https://vk.com/dev/methods)
* [Я в Telegram](https://t.me/bio_major4ik)



```python

from vka import API
import asyncio


async def main():
    api = API(token='token')
    await api.async_init()  # открывает сессию для работы, без этого не работает
    # Есть два варианта обращение к API методам отличие лишь в написание
    # первый вариант
    users_get = await api.method('users.get', {'user_ids': 1})
    # второй вариант
    users_get = api.users.get(user_ids=1)

    # обязательно нужно закрыть сессию иначе будет вылезать ошибка о не закрытой сессию
    await api.close()


asyncio.run(main())

```