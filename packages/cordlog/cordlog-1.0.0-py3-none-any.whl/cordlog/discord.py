import asyncio
import logging
from .utils import publish_message


class DiscordHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.loop = asyncio.get_event_loop()

    def emit(self, record):
        try:
            msg = self.format(record)
            publish_message(msg)
        except Exception:
            self.handleError(record)
