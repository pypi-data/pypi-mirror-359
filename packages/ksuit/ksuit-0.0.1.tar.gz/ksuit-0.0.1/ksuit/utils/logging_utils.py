import logging
import sys
from collections import defaultdict


class MessageCounter(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(type(self).__name__)
        self.min_level = logging.WARNING
        self.counts = defaultdict(int)

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno >= self.min_level:
            self.counts[record.levelno] += 1

    def log(self) -> None:
        for level in [logging.WARNING, logging.ERROR]:
            self.logger.info(f"encountered {self.counts[level]} {logging.getLevelName(level).lower()}s")


def initialize(is_rank0: bool, log_file_uri: str) -> MessageCounter:
    logger = logging.getLogger()
    logger.handlers = []
    # add_stdout_handler sets level to logging.INFO
    if is_rank0:
        _add_handler(logging.StreamHandler(stream=sys.stdout))
        _add_handler(logging.FileHandler(log_file_uri, mode="a"))
    else:
        # subprocesses log warnings to stderr --> logging.CRITICAL prevents this
        logger.setLevel(logging.CRITICAL)
    return _add_handler(MessageCounter())


def _add_handler(handler: logging.Handler) -> logging.Handler:
    logger = logging.getLogger()
    handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s %(levelname).1s %(message)s",
        datefmt="%m-%d %H:%M:%S",
    ))
    logger.handlers.append(handler)
    return handler
