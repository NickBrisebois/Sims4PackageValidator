import os
from pathlib import Path
from typing import Generator

from package_validator import PackageFile

PACKAGE_EXTENSIONS = [".package"]
SCRIPT_EXTENSIONS = [".t4script"]


def find_package_files(directory: Path) -> Generator[PackageFile, None, None]:
    for root, subdirs, files in os.walk(directory, topdown=True):
        for subdir in subdirs:
            yield from find_package_files(Path(subdir))

        for file in files:
            yield PackageFile(file_path=Path(root) / file, file_name=file)
