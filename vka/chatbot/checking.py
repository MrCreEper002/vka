import inspect
import asyncio
import json

from loguru import logger

from vka.base import AttrDict
from vka.chatbot.context import Context


class CheckingEventForCommand:

    def __init__(
            self, ctx: Context,
            menu_commands: list,
            callback_action: dict,
            commands: list
    ):
        self._ctx = ctx
        self.menu_commands = menu_commands
        self.callback_action = callback_action
        self.commands = commands

    async def search_for_command_message(
            self
    ):
        await self.checking_command_in_menu()
        await self.checking_message_in_all_commands()

    async def checking_command_in_menu(self, obj=None, data: bool = False):
        if data:
            try:
                command = obj.payload.command
                argument = obj.payload.args
            except (KeyError, AttributeError):
                return
            for i in self.menu_commands:
                for j in i['menu']:
                    if j['category'] == argument or j['subcategory'] == argument:
                        await self.init_func(
                            i['func_obj'], self._ctx,
                            command=command, argument=i['button']
                        )
            return

        for i in self.menu_commands:
            cmd = self._ctx.msg.text.lower().split(' ')[
                  0:len(i['command'].split(' '))
                ]
            logger.debug(i['button'])
            if i['command'] in cmd:
                await self.init_func(
                    func=i['func_obj'],
                    ctx=self._ctx,
                    command=cmd,
                    argument=i['button']
                )

    async def checking_message_in_all_commands(self):
        """ Проверка на наличие команды во всех командах """
        for command in self.commands:
            cmd = ''
            match command['commands']:
                case _command if type(_command) is str:
                    cmd = self._ctx.msg.text.lower().split(' ')[
                          0:len(command['commands'].split(' '))
                          ]

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
                        argument=self._ctx.msg.text.lower().replace(
                            _command, ''
                        ).strip()
                    )
                    continue
                case {
                    'commands': _command
                      } if ''.join(_command) == self._ctx.msg.text:
                    await self.init_func(
                        func=command['func_obj'],
                        ctx=self._ctx,
                        command=cmd,
                        custom_answer=command['custom_answer']
                    )
                    continue

    async def shipment_data_message_event(self, obj):
        """
        Обрабатывает нажатие на кнопку
        """
        await self.checking_command_in_menu(obj=obj, data=True)
        event_data = {}
        try:
            command = obj.payload.command
            argument = obj.payload.args
        except (KeyError, AttributeError):
            try:
                argument = AttrDict(eval(obj.message.payload))
                command = eval(obj.message.payload)['command']
            except (KeyError, AttributeError):
                return
        saved_command = self.callback_action.get(command)
        if saved_command:
            if saved_command.get('click'):
                return await self.init_func(
                    saved_command['func_obj'], self._ctx,
                    command=command, argument=argument
                )
            if saved_command['callback']:
                await self.init_func(
                    saved_command['func_obj'], self._ctx,
                    command=command, argument=argument
                )
            if saved_command['show_snackbar']:
                argument = argument if argument != '' else None
                argument = argument if argument != () else None
                event_data['type'] = 'show_snackbar'
                event_data = await self._inspect_signature_executions(
                    self._ctx, saved_command['func_obj'], event_data,
                    argument=argument
                )
        else:
            gather = []
            for func in self.commands:
                if func['func_obj'].__name__ == command:
                    # ctx.cmd = func['commands'][-1] \
                    #     if type(func['commands']) is list \
                    #     else func['commands']

                    if func['show_snackbar'] is not None:
                        event_data['type'] = 'show_snackbar'
                        event_data['text'] = func['show_snackbar']
                        gather.append(
                            self._ctx.api.method(
                                'messages.sendMessageEventAnswer',
                                {
                                    "event_id": obj.event_id,
                                    "user_id": obj.user_id,
                                    "peer_id": obj.peer_id,
                                    "event_data": json.dumps(event_data)
                                }
                            )
                        )
                    gather.append(
                        self.init_func(
                            func['func_obj'], self._ctx,
                            command=command, argument=argument
                        )
                    )
                    await asyncio.gather(*gather)
                    return

        if event_data == {}:
            return
        return await self._ctx.api.method(
            'messages.sendMessageEventAnswer',
            {
                "event_id": obj.event_id,
                "user_id": obj.user_id,
                "peer_id": obj.peer_id,
                "event_data": json.dumps(event_data)
            }
        )

    @staticmethod
    async def _inspect_signature_executions(
            ctx: Context, func, event_data: dict, argument: str
    ):
        parameters = inspect.signature(
            func
        ).parameters
        if len(parameters) == 0:
            event_data['text'] = await func()
        elif len(parameters) == 1:
            event_data['text'] = await func(ctx)
        else:
            event_data['text'] = await func(ctx, argument)
        return event_data

    @staticmethod
    async def init_func(
            func,
            ctx: Context,
            command: str | list,
            argument: str = '',
            custom_answer: str = None
    ) -> asyncio.create_task:
        ctx.command = ''.join(command)
        if custom_answer is not None:
            return await ctx.answer(custom_answer)
        argument = argument if argument != '' else None
        argument = argument if argument != () else None
        sig = inspect.signature(func)

        parameters = [
            p for p in sig.parameters.keys()
            if p not in ['kwargs', 'args']
        ]

        if len(parameters) == 0 and argument is None:
            return asyncio.create_task(func())
        elif len(parameters) == 1 and argument is not None:
            try:
                return asyncio.create_task(func(ctx, argument))
            except TypeError:
                return asyncio.create_task(func(ctx))
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
                argument=self._ctx.msg.text.lower().replace(cmd, '').strip()
            )
