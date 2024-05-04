# Ожидание сообщения


```python
def cancel(): ...


@bot.add_command(commands='поиск')
async def greet(ctx: Context):
    keyboard = Keyboard(
        Button.callback('Отмена️').secondary().on_called(
            cancel,
        ),
        inline=True
    )
    await ctx.answer('тык', keyboard=keyboard)
    # чтобы получать в этой команде дальше новые сообщение для других данных
    # если указать параметр `any_user=True` то будет получать сообщение от всех пользователей
    async for new_ctx in ctx.receive_new_message():
        # если нужно завершить по нажатию кнопки
        if new_ctx.button_checking(cancel, ctx.msg.from_id):
            break
        # если кнопка не нажата то дальше логика 
```