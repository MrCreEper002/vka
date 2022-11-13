import inspect
from loguru import logger
import asyncio

from vka.base import AttrDict
from vka.chatbot.context import Context


class CheckingMessageForCommand:

    def __init__(self, ctx: Context):
        self._ctx = ctx

    async def check_message(
            self, all_commands: list
    ):

        for command in all_commands:
            cmd = ''
            match command['commands']:
                case _command if type(_command) is str:
                    cmd = self._ctx.msg.text.lower().split(' ')[0:len(command['commands'].split(' '))]

            match command:
                case {'any_text': True}:
                    await self.init_func(
                        func=command['func_obj'],
                        ctx=self._ctx,
                        command=cmd,
                    )
                    continue
                case {'commands': _command} if type(_command) is tuple:
                    await self._checking_for_list(command)
                    continue
                case {'commands': _command} if _command in cmd:
                    self._ctx.command = _command
                    await self.init_func(
                        func=command['func_obj'],
                        ctx=self._ctx,
                        command=cmd,
                        argument=self._ctx.msg.text.lower().replace(_command, '').strip()
                    )
                    continue
                case {'commands': _command} if ''.join(_command) == self._ctx.msg.text:
                    await self.init_func(
                        func=command['func_obj'],
                        ctx=self._ctx,
                        command=cmd,
                        custom_answer=command['custom_answer']
                    )
                    continue

    @staticmethod
    async def init_func(
            func,
            ctx: Context,
            command: str,
            argument: str = '',
            custom_answer: str = None
    ) -> asyncio.create_task:
        ctx.command = ''.join(command)
        if custom_answer is not None:
            return await ctx.answer(custom_answer)
        argument = argument if argument != '' else None
        argument = argument if argument != () else None
        parameters = inspect.signature(func).parameters

        if len(parameters) == 0 and argument is None:
            return asyncio.create_task(func())
        elif len(parameters) == 1 and argument is None:
            return asyncio.create_task(func(ctx))
        elif len(parameters) == 2:
            return asyncio.create_task(func(ctx, argument))
        else:
            return

    async def _checking_for_list(self, command: AttrDict):
        cmd = ''.join(
            [
                i
                for i in command['commands']
                if i in ' '.join(
                    self._ctx.msg.text.lower().split(' ')[0:len(i.split(' '))]
                )
            ]
        )
        if cmd in command['commands']:
            await self.init_func(
                func=command['func_obj'],
                ctx=self._ctx,
                command=cmd,
                argument=self._ctx.msg.text.replace(cmd, '').strip()
            )
