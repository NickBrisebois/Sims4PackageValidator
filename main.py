from argparse import ArgumentParser
from pathlib import Path

from files import find_package_files
from log_handler import LogHandler
from package_validator import SimsPackageValidator


def main():
    # for root, subdirs, files in os.walk()
    parser = ArgumentParser(description="Package Checker")
    parser.add_argument("-d", "--directory", type=Path, help="Directory to check")
    parser.add_argument("-o", "--outdir", type=Path, help="Output directory")
    args = parser.parse_args()

    logger = LogHandler.get_logger(__name__)
    package_validator = SimsPackageValidator(logger)

    for package_file in find_package_files(args.directory):
        package_validator.validate(package_file)
        print(package_file.file_path)


if __name__ == "__main__":
    main()
