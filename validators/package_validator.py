import struct
from dataclasses import dataclass
from enum import Enum
from logging import Logger

import validators.magic_numbers.packages as magic
from files import CCFile
from validators.base_validator import BaseValidator


class ValidationError(Enum):
    # Common meta file errors
    FILE_TOO_SMALL = "FILE_TOO_SMALL"

    INVALID_FILE_IDENTIFIER = "MISSING_FILE_IDENTIFIER"
    INVALID_FORMAT_VERSION = "INVALID_FORMAT_VERSION"
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
    index_offset_long: int
    unknown_four: bytes


class PackageException(Exception):
    detail: str
    error: ValidationError

    def __init__(self, detail: str, error: ValidationError):
        self.detail = detail
        self.error = error


class SimsPackageValidator(BaseValidator):
    _logger: Logger

    def __init__(self, logger: Logger):
        self._logger = logger

    def _verify_file_meta(self, package_file: CCFile) -> None:
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
        # Unpack header data
        # ref: https://docs.python.org/3/library/struct.html#format-characters
        # ref: https://thesims4moddersreference.org/reference/dbpf-format/
        vals = struct.unpack("<4s 11I 12s I Q 24s", header_data)

        (
            file_signature,
            major_format_version,
            minor_format_version,
            major_file_version,  # unused
            minor_file_version,  # unused
            unknown_one,  # unused
            creation_time,  # unused
            update_time,  # unused
            unknown_two,  # unused
            index_count,
            index_offset_short,
            index_size,
            unknown_three,  # unused
            unknown_four,  # unused
            index_offset_long,
            unknown_five,  # unused
        ) = vals

        return DBPFHeader(
            file_signature=file_signature,
            major_file_version=major_format_version,
            minor_file_version=minor_format_version,
            major_format_version=major_format_version,
            minor_format_version=minor_format_version,
            unknown_one=unknown_one,
            creation_time=creation_time,
            update_time=update_time,
            unknown_two=unknown_two,
            index_count=index_count,
            index_offset_short=index_offset_short,
            index_size=index_size,
            unknown_three=unknown_three,
            index_offset_long=index_offset_long,
            unknown_four=unknown_four,
        )

    def validate(self, package_file: CCFile):
        try:
            self._verify_file_meta(package_file)

            with package_file.file_path.open("rb") as raw_package:
                header_data = raw_package.read(magic.HEADER_SIZE)
                header = self._parse_dbpf2_header(header_data)

                if header.file_signature != magic.FILE_IDENTIFIER:
                    self._logger.error(
                        f"File is not a valid DBPF file: {package_file.file_path}"
                    )
                    return ValidationError.INVALID_FILE_IDENTIFIER
                if (
                    header.major_format_version != magic.EXPECTED_MAJOR_FORMAT_VERSION
                    or header.minor_format_version
                    != magic.EXPECTED_MINOR_FORMAT_VERSION
                ):
                    self._logger.error(
                        f"Invalid major/minor format version values: {package_file.file_path}"
                    )
                    return ValidationError.INVALID_FORMAT_VERSION

            self._logger.info(f"Package file is good! 😎: {package_file.file_path}")

        except PackageException as e:
            self._logger.error(f"Error validating package: {e.detail}")
            return e.error
        except Exception as e:
            self._logger.error(f"Unknown error while validating package: {e}")
            return ValidationError.UNKNOWN_ERROR
