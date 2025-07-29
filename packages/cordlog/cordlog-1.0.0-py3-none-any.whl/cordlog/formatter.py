import logging
import copy

TRACE = logging.DEBUG - 5
CORE = logging.INFO + 5

COLORS = {
    'WARNING': 33,
    'INFO': 32,
    'DEBUG': 34,
    'CRITICAL': 35,
    'ERROR': 31,
    'TRACE': 36,
    'CORE': 35
}

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"


def colorize(level, text):
    color = COLORS.get(level, 37)
    return COLOR_SEQ % color + text + RESET_SEQ


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        record_copy = copy.copy(record)
        record_copy.levelname = colorize(record.levelname, record.levelname)
        return super().format(record_copy)
