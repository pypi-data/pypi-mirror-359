import logging
import logging.config
from typing import Optional, overload

from aiohttp import ClientSession
from .formatter import ColoredFormatter
from .discord import DiscordHandler
from .logger import LordLogger, TRACE, CORE
from . import storage


@overload
def setup_storage(
    webhook_url: Optional[str] = ...,
    session: Optional[ClientSession] = ...
) -> None: ...


def setup_storage(**kwargs):
    for k, v in kwargs.items():
        setattr(storage, k, v)


def setup_logging(config: dict):
    logging.setLoggerClass(LordLogger)
    logging.addLevelName(TRACE, "TRACE")
    logging.addLevelName(CORE, "CORE")
    logging.config.dictConfig(config)
