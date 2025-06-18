import logging
from enum import Enum
from typing import Any, Dict
from colorama import Fore, Style, init

init(autoreset=True)

# Custom SUCCESS log level
SUCCESS_LEVEL_NUM = 25
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")


def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kwargs)


logging.Logger.success = success


class LogLevel(Enum):
    DEBUG = (Fore.MAGENTA, "DEBUG")
    INFO = (Fore.BLUE, "INFO")
    SUCCESS = (Fore.LIGHTGREEN_EX, "SUCCESS")
    WARNING = (Fore.YELLOW, "WARNING")
    ERROR = (Fore.LIGHTRED_EX, "FAILURE")
    CRITICAL = (Fore.RED, "CRITICAL")


class CustomFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        color, _ = (
            LogLevel[record.levelname].value
            if record.levelname in LogLevel.__members__
            else ("", "")
        )
        prefix = f"{color}[{record.levelname:^10}]{Style.RESET_ALL} -{Fore.LIGHTGREEN_EX} [ CS-LB ] {Fore.WHITE}>{Style.RESET_ALL}"
        return f"{prefix} {record.getMessage()}{Style.RESET_ALL}"


class Logger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setFormatter(CustomFormatter())
        self.logger.addHandler(handler)

    def _log_captcha(self, level: LogLevel, data: Dict[str, Any]):
        msg = (
            f"{Fore.LIGHTBLUE_EX}TOKEN:{Style.RESET_ALL} {data['token']:>35} | "
            f"{Fore.LIGHTWHITE_EX}WAVES:{Style.RESET_ALL} {data['waves']:>3} | "
            f"{Fore.LIGHTCYAN_EX}VARIANT:{Style.RESET_ALL} {data['variant'].upper():>12}"
        )
        getattr(self.logger, level.name.lower())(msg)

    def solved_captcha(self, token: str, waves: Any, variant: str):
        self._log_captcha(LogLevel.SUCCESS, {
            "token": token,
            "waves": waves,
            "variant": variant,
        })

    def failed_captcha(self, token: str, waves: Any, variant: str):
        self._log_captcha(LogLevel.ERROR, {
            "token": token,
            "waves": waves,
            "variant": variant,
        })

    def log_info(self, message: str):
        self.logger.info(message)

    def log_debug(self, message: str):
        self.logger.debug(message)


log = Logger(__name__)