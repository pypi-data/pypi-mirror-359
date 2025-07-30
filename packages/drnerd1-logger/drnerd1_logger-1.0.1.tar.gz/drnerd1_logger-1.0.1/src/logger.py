"""

A Custom Logging Module

"""

import sys
import logging
import colorlog
import colorama

colorama.init(strip=False)

LOG_FILE_LOCATION = "../logs.log"


class CustomColoredFormatter(colorlog.ColoredFormatter):
    CUSTOM_ANSI_COLORS = {
        'DEBUG': '\033[36m',  # cyan
        'INFO': '\033[1;94m',  # deep bright blue
        'WARNING': '\033[33m',  # yellow
        'ERROR': '\033[31m',  # red
        'CRITICAL': '\033[1;31m',  # bold red
    }
    WHITE = '\033[97m'  # bright white
    GREEN = '\033[32m'
    GRAY = '\033[90m'
    MAGENTA = '\033[35m'
    def format(self, record):
        reset = '\033[0m'
        level_color = self.CUSTOM_ANSI_COLORS.get(record.levelname, '')
        record.colored_levelname = f"{level_color}{record.levelname:<8}{reset}{self.WHITE}"
        record.colored_asctime = f"{self.GREEN}{self.formatTime(record, self.datefmt)}{reset}"
        return super().format(record)


stdout_handler = colorlog.StreamHandler(stream=sys.stdout)
stdout_handler.setFormatter(CustomColoredFormatter('[%(colored_asctime)s] %(colored_levelname)s %(message)s'))

file_handler = logging.FileHandler(LOG_FILE_LOCATION)

logger = colorlog.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(stdout_handler)
logger.addHandler(file_handler)
