import logging

import colorlog


class LogHandler:
    @classmethod
    def get_logger(cls, name: str):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)s:%(name)s:%(message)s%(reset)s",
            datefmt=None,
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={},
            style="%",
        )

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        return logger
