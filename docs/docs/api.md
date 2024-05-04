# API

Использование API

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