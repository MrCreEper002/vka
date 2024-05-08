
<p align="center">
  <a href="https://github.com/MrCreEper002/vka">
    <img height="150px" alt="vka" src="https://raw.githubusercontent.com/MrCreEper002/vka/master/docs/logo.png">
  </a>
</p>
<h1 align="center">
  vka 
</h1>
<p align="center">
    <em><b>инструмент для создания ботов для ВКонтакте на Python</b></em>
</p>

***
[![PyPI](https://img.shields.io/pypi/v/vka.svg)](https://pypi.org/project/vka/) ![Python 3.x](https://img.shields.io/pypi/pyversions/vka.svg)
***
![Static Badge](https://img.shields.io/badge/MrCreEper002-vka-vka)
![GitHub top language](https://img.shields.io/github/languages/top/MrCreEper002/vka)
![GitHub](https://img.shields.io/github/license/MrCreEper002/vka)
![GitHub Repo stars](https://img.shields.io/github/stars/MrCreEper002/vka)
[![Documentation Status](https://readthedocs.org/projects/vka/badge/?version=latest)](https://vka.readthedocs.io/ru/latest/?badge=latest)

#### Модуль сделана по основам [vk_api](https://github.com/python273/vk_api) и [vkquick](https://github.com/deknowny/vkquick)

[//]: # (***)
# Установка 
```shell
pip install vka
```
[//]: # ([![Typing SVG]&#40;https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=pip+install+vka&#41;]&#40;https://git.io/typing-svg&#41;)

# Полезная информация
* __Информация о _API___
  * __[API](https://dev.vk.com/ru)__
* __Информация о _vka___
  * __[Документация](https://vka.readthedocs.io/ru/latest/?badge=latest)__
  * __[Официальный канал в Telegram](https://t.me/vka_official)__
***

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