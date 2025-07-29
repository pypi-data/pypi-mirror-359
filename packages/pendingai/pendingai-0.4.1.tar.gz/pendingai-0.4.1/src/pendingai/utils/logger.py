#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

from pendingai.abc import Singleton

LOGGER_NAME: str = "pendingai"
LOGGER_FORMATTER: str = (
    "[%(name)s] %(asctime)s - %(levelname)s "
    "[%(filename)s:%(funcName)s:%(lineno)s] %(message)s"
)


class Logger(Singleton):
    _logfile: str = "pai.log"
    _logfile_size: int = int(5 * 1e6)
    _logfile_backups: int = 3

    def _initialize(self, level: int | str = logging.WARNING) -> None:
        """
        Initialize singletone logger configuration called on setup.
        """
        self._logger: logging.Logger = logging.getLogger(LOGGER_NAME)
        self._logger.setLevel(level)
        self._logger.propagate = False

        # setup both console stream handler and rotating file logger for
        # debugging purposes and helping when a user encounters runtime
        # errors and need to submit bug reports
        if not self._logger.handlers:
            formatter = logging.Formatter(LOGGER_FORMATTER)
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            log_file_path = Path.home() / ".pendingai" / self._logfile
            log_file_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=self._logfile_size,
                backupCount=self._logfile_backups,
            )
            file_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)
            self._logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        """
        Retrieve singleton formatter logger instance.
        """
        return self._logger
