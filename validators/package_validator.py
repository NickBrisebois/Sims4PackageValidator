import struct
from dataclasses import dataclass
from enum import Enum
from io import BufferedReader
from logging import Logger
from pathlib import Path

import validators.magic_numbers.packages as magic
from files import CCFile, CCType
from validators.base_validator import BaseValidator


class ValidationError(Enum):
    # General file errors
    FILE_TOO_SMALL = "FILE_TOO_SMALL"

    # File header issues
    INVALID_FILE_IDENTIFIER = "MISSING_FILE_IDENTIFIER"
    INVALID_FORMAT_VERSION = "INVALID_FORMAT_VERSION"
    INVALID_UNKNOWN_CONSTANT = "INVALID_UNKNOWN_CONSTANT"

    # Index issues
    INDEX_OUT_OF_BOUNDS = "INDEX_OUT_OF_BOUNDS"
    EMPTY_INDEX_INFO = "EMPTY_INDEX_INFO"
    INVALID_INDEX = "INVALID_INDEX"
    INDEX_PARSE_ERROR = "INDEX_PARSE_ERROR"

    # idk how these would even happen but ¯\_(ツ)_/¯
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_NOT_FILE = "FILE_NOT_FILE"

    UNKNOWN_ERROR = "UNKNOWN_ERROR"


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
    unknown_constant: int
    index_offset_long: int
    padding: bytes


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

    def _parse_dbpf2_header(self, header_data: bytes) -> DBPFHeader:
        # Unpack header data
        vals = struct.unpack(magic.HEADER_STRUCT_FORMAT, header_data)

        (
            file_signature,
            major_format_version,
            minor_format_version,
            major_file_version,  # unused
            minor_file_version,  # unused
            unknown_one,  # unused
            creation_time,  # unused
            update_time,  # unused
            unknown_two,  #
            index_count,
            index_offset_short,
            index_size,
            unknown_three,  # unused
            unknown_constant,  # unknown but always uint32 w/ val 3
            index_offset_long,
            padding,  # unused
        ) = vals

        return DBPFHeader(
            file_signature=file_signature,
            major_format_version=major_format_version,
            minor_format_version=minor_format_version,
            major_file_version=major_file_version,
            minor_file_version=minor_file_version,
            unknown_one=unknown_one,
            creation_time=creation_time,
            update_time=update_time,
            unknown_two=unknown_two,
            index_count=index_count,
            index_offset_short=index_offset_short,
            index_size=index_size,
            unknown_three=unknown_three,
            unknown_constant=unknown_constant,
            index_offset_long=index_offset_long,
            padding=padding,
        )

    def validate_file_meta(self, package_file: CCFile) -> None:
        """
        Just make sure we're working on a real file
        """
        error_code = None
        error_msg = None

        if package_file.file_type != CCType.PACKAGE:
            error_msg = (
                f"Incorrect file passed to SimsPackageValidator: {package_file.file_path}. "
                + "This is a programming error and not an issue with the file itself"
            )
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        if not package_file.file_path.exists():
            error_msg = f"File does not exist: {package_file.file_path}"
            error_code = ValidationError.FILE_NOT_FOUND
            self._logger.error(error_msg)

        if not package_file.file_path.is_file():
            error_msg = f"Path is not a file: {package_file.file_path}"
            error_code = ValidationError.FILE_NOT_FILE
            self._logger.error(error_msg)

        if package_file.file_path.stat().st_size < magic.MIN_FILE_SIZE:
            error_msg = f"File is too small: {package_file.file_path}"
            error_code = ValidationError.FILE_TOO_SMALL
            self._logger.error(error_msg)

        if error_code and error_msg:
            raise PackageException(
                detail=error_msg,
                error=error_code,
            )

    def validate_header(
        self, file_path: Path, header: DBPFHeader
    ) -> ValidationError | None:
        error_msg = None
        error_code = None

        if header.file_signature != magic.FILE_IDENTIFIER:
            error_msg = f"File is not a valid DBPF file: {file_path}"
            error_code = ValidationError.INVALID_FILE_IDENTIFIER

        if (
            header.major_format_version != magic.EXPECTED_MAJOR_FORMAT_VERSION
            or header.minor_format_version != magic.EXPECTED_MINOR_FORMAT_VERSION
        ):
            error_msg = f"Invalid major/minor format version values: {file_path}"
            error_code = ValidationError.INVALID_FORMAT_VERSION

        if header.unknown_constant != magic.EXPECTED_UNKNOWN_CONSTANT:
            error_msg = f"Invalid unknown constant value: {file_path}"
            error_code = ValidationError.INVALID_UNKNOWN_CONSTANT

        if error_code and error_msg:
            raise PackageException(
                detail=error_msg,
                error=error_code,
            )

    def validate_index_info(
        self,
        raw_package_data: BufferedReader,
        package_file: CCFile,
        header: DBPFHeader,
        file_size_bytes: int,
    ):
        error_msg = None
        error_code = None

        if header.index_size == 0:
            error_msg = f"Index info is empty: {package_file.file_path}"
            error_code = ValidationError.EMPTY_INDEX_INFO

        if (
            header.index_offset_short > file_size_bytes
            or header.index_offset_short + header.index_size > file_size_bytes
        ):
            error_msg = f"Index info is out of bounds: {package_file.file_path}"
            error_code = ValidationError.INDEX_OUT_OF_BOUNDS

        try:
            raw_package_data.seek(header.index_offset_short)
            index_data = raw_package_data.read(header.index_size)

            if len(index_data) != header.index_size:
                error_msg = f"Couldn't read complete index (expected {header.index_size} bytes, got {len(index_data)} bytes)"
                error_code = ValidationError.INVALID_INDEX
        except Exception as e:
            error_msg = f"Failed to parse index info: {package_file.file_path}"
            error_code = ValidationError.INDEX_PARSE_ERROR

        if error_msg and error_code:
            raise PackageException(
                detail=error_msg,
                error=error_code,
            )

    def validate(self, package_file: CCFile):
        try:
            self.validate_file_meta(package_file)

            with package_file.file_path.open("rb") as raw_package:
                header_data = raw_package.read(magic.HEADER_SIZE)
                header = self._parse_dbpf2_header(header_data)

                if error := self.validate_header(package_file.file_path, header):
                    return error

                if error := self.validate_index_info(
                    raw_package_data=raw_package,
                    package_file=package_file,
                    header=header,
                    file_size_bytes=package_file.file_size_bytes,
                ):
                    return error

            self._logger.info(f"Package file is good! 😎: {package_file.file_path}")

        except PackageException as e:
            self._logger.error(f"Error validating package: {e.detail}")
            return e.error
        except ValueError:
            raise
        except Exception as e:
            self._logger.error(f"Unknown error while validating package: {e}")
            return ValidationError.UNKNOWN_ERROR
