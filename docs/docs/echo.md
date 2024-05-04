# Эхо-Бот

Самая простая команда для того чтобы бот повторял все что ты пишешь.

```python
from vka import ABot, Context

bot = ABot(token='group_token')


@bot.add_command(any_text=True)
async def echo(ctx: Context):
    await ctx.answer(ctx.msg.text)

bot.run()

```