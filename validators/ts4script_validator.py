from logging import Logger

from files import PackageFile
from validators.base_validator import BaseValidator


class TS4ScriptValidator(BaseValidator):
    _logger: Logger

    def __init__(self, logger: Logger):
        self._logger = logger

    def validate(self, package_file: PackageFile) -> None:
        self._logger.debug("[NOT IMPLEMENTED] Validating TS4Script file")
