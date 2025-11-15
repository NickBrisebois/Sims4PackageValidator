import struct
from dataclasses import _MISSING_TYPE, dataclass
from enum import Enum
from logging import Logger
from multiprocessing import Value
from pathlib import Path

import magic_package_values as magic


@dataclass
class PackageFile:
    file_path: Path
    file_name: str


class ValidationError(Enum):
    # Common meta file errors
    FILE_TOO_SMALL = "FILE_TOO_SMALL"

    MISSING_FILE_IDENTIFIER = "MISSING_FILE_IDENTIFIER"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

    # How?
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_NOT_FILE = "FILE_NOT_FILE"


@dataclass
class DBPFHeader:
    file_signature: bytes
    major_format_version: int
    minor_format_version: int
    major_file_version: int
    minor_file_version: int
    unknown_one: int
    creation_time: int
    update_time: int
    unknown_two: int
    index_count: int
    index_offset_short: int
    index_size: int
    unknown_three: bytes
    unknown_four: int
    index_offset_long: int
    unknown_five: bytes


class PackageException(Exception):
    detail: str
    error: ValidationError

    def __init__(self, detail: str, error: ValidationError):
        self.detail = detail
        self.error = error


class SimsPackageValidator:
    _logger: Logger

    def __init__(self, logger: Logger):
        self._logger = logger

    def _verify_file_meta(self, package_file: PackageFile) -> None:
        """
        Just make sure we're working on a real file
        """
        error_code = None
        error_msg = None

        if not package_file.file_path.exists():
            error_msg = f"File does not exist: {package_file.file_path}"
            error_code = ValidationError.FILE_NOT_FOUND
            self._logger.error(error_msg)

        if not package_file.file_path.is_file():
            error_msg = f"Path is not a file: {package_file.file_path}"
            self._logger.error(error_msg)
            raise PackageException(
                detail=error_msg,
                error=ValidationError.FILE_NOT_FILE,
            )

        if package_file.file_path.stat().st_size < magic.MIN_FILE_SIZE:
            error_msg = f"File is too small: {package_file.file_path}"
            error_code = ValidationError.FILE_TOO_SMALL
            self._logger.error(error_msg)
            raise PackageException(
                detail=error_msg,
                error=ValidationError.FILE_TOO_SMALL,
            )

        if error_code and error_msg:
            raise PackageException(
                detail=error_msg,
                error=error_code,
            )

    def _parse_dbpf2_header(self, header_data: bytes) -> DBPFHeader:
        # Unpack header data in this format:
        # < (little endian)
        # 4s (4 byte char, for file identifier)
        # I (4 byte unsigned integer, for major format version)
        # I (4 byte unsigned integer, for minor format version)
        # I (4 byte unsigned integer, major file version, unused)
        # I (4 byte unsigned integer, minor file version, unused)
        # I (4 byte unsigned integer, unknown, unused)
        # I (4 byte unsigned integer, creation time, unused)
        # I (4 byte unsigned integer, update time, unused)
        # I (4 byte unsigned integer, unknown, unused)
        # I (4 byte unsigned integer, index offset, short (absolute) [1])
        # I (4 byte unsigned integer, index size)
        # 12s (12 byte char, unknown, unused)
        # I (4 byte unsigned integer, unknown, unused)
        # 2I (8 byte unsigned integer, unknown, unused)
        values = struct.unpack("<4sIIIIIIIIII12sI2I2I", header_data)
        return DBPFHeader(*values)

    def validate(self, package_file: PackageFile):
        try:
            self._verify_file_meta(package_file)

            with package_file.file_path.open("rb") as raw_package:
                header_data = raw_package.read(magic.HEADER_SIZE)
                header = self._parse_header(header_data)

                if header.file_signature != magic.FILE_IDENTIFIER:
                    self._logger.error(
                        f"File is not a valid DBPF file: {package_file.file_path}"
                    )
                    return ValidationError.MISSING_FILE_IDENTIFIER

            self._logger.info(f"Package file is good! 😎: {package_file.file_path}")

        except PackageException as e:
            self._logger.error(f"Error validating package: {e.detail}")
            return e.error
        except Exception as e:
            self._logger.error(f"Unknown error while validating package: {e}")
            return ValidationError.UNKNOWN_ERROR
