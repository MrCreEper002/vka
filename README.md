# vk-a

~~~python
from vka import Bot, Validator

# токен от ГРУППЫ
bot = Bot("group_token")

# добавление команды в бота
@bot.command(names='test')
async def test(ctx: Validator):
    # чтобы отлавливать только новые сообщения
    if ctx.type_message == 'message_new':
        # чтобы воспользоваться методом
        await ctx.api.users.get(user_ids=1)
        # отправка сообщения
        await ctx.answer('test :)')

# запуск бота
bot.run(True)
~~~