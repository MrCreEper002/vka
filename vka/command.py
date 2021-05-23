from typing import Iterable

from vka.storage_box import storage_box


class Commands:
    def __init__(
            self,
            names: Iterable[str] = (),
            prefixes: Iterable[str] = (),
            any_text: bool = False,
    ):
        self._names = names
        self._prefixes = prefixes
        self._any_text = any_text

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            storage_box.commands.append(
                {
                    'func_obj': func,
                    'any_text': self._any_text,
                    'names': self._names,
                    'prefixes': self._prefixes
                }
            )
            # logger.info(inspect.signature(func))

            # for name, argument in inspect.signature(func).parameters.items():
            #     logger.info(f"{name} {argument.annotation}")
            print(args, kwargs)
            return func
        return wrapper
