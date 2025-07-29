import logging

TRACE = logging.DEBUG - 5
CORE = logging.INFO + 5


class LordLogger(logging.Logger):
    def __init__(self, name: str, level: int = logging.NOTSET):
        super().__init__(name, level)

    def trace(self, msg, *args, **kwargs):
        if self.isEnabledFor(TRACE):
            self._log(TRACE, msg, args, **kwargs)

    def core(self, msg, *args, **kwargs):
        if self.isEnabledFor(CORE):
            self._log(CORE, msg, args, **kwargs)
