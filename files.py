import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Generator

PACKAGE_EXTENSIONS = (".package",)
SCRIPT_EXTENSIONS = (".t4script",)
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif")


class CCType(Enum):
    PACKAGE = "package"
    SCRIPT = "script"
    IMAGE = "image"


MAPPING = {
    PACKAGE_EXTENSIONS: CCType.PACKAGE,
    SCRIPT_EXTENSIONS: CCType.SCRIPT,
    IMAGE_EXTENSIONS: CCType.IMAGE,
}


@dataclass
class PackageFile:
    file_path: Path
    file_name: str
    file_type: CCType


def find_package_files(directory: Path) -> Generator[PackageFile, None, None]:
    for root, subdirs, files in os.walk(directory, topdown=True):
        for subdir in subdirs:
            yield from find_package_files(Path(subdir))

        for file in files:
            for ext, type in MAPPING.items():
                if file.endswith(ext):
                    yield PackageFile(
                        file_path=Path(root) / file,
                        file_name=file,
                        file_type=type,
                    )
