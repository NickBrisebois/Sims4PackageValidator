import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Generator

PACKAGE_EXTENSIONS = (".package",)
SCRIPT_EXTENSIONS = (".ts4script",)
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif")


class CCType(Enum):
    PACKAGE = "PACKAGE"
    SCRIPT = "SCRIPT"
    IMAGE = "IMAGE"
    OTHER = "OTHER"


MAPPING = {
    PACKAGE_EXTENSIONS: CCType.PACKAGE,
    SCRIPT_EXTENSIONS: CCType.SCRIPT,
    IMAGE_EXTENSIONS: CCType.IMAGE,
}


@dataclass
class CCFile:
    file_path: Path
    relative_path: Path
    file_name: str
    file_type: CCType
    file_size_bytes: int


def find_cc_files(directory: Path) -> Generator[CCFile, None, None]:
    for root, subdirs, files in os.walk(directory, topdown=True):
        for subdir in subdirs:
            yield from find_cc_files(Path(subdir))

        for file in files:
            file_type = CCType.OTHER
            for ext, type in MAPPING.items():
                if file.endswith(ext):
                    file_type = type

            file_path = Path(root) / file
            yield CCFile(
                file_path=file_path,
                relative_path=file_path.relative_to(directory),
                file_name=file,
                file_type=file_type,
                file_size_bytes=file_path.stat().st_size,
            )


def write_file_to_output(cc_file: CCFile, output_dir: Path):
    output_path = output_dir / cc_file.relative_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(cc_file.file_path.read_bytes())
