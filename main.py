from argparse import ArgumentParser
from pathlib import Path

from files import find_package_files
from log_handler import LogHandler
from validators.package_validator import SimsPackageValidator


def main():
    # for root, subdirs, files in os.walk()
    parser = ArgumentParser(description="Package Checker")
    parser.add_argument("-d", "--directory", type=Path, help="Directory to check")
    parser.add_argument("-o", "--outdir", type=Path, help="Output directory")
    args = parser.parse_args()

    logger = LogHandler.get_logger(__name__)
    package_validator = SimsPackageValidator(logger)

    corrupted = 0
    valid = 0

    for package_file in find_package_files(args.directory):
        if error := package_validator.validate(package_file):
            logger.error(f"Validation error for {package_file}: {error}")
            corrupted += 1
        else:
            valid += 1
            logger.info(f"Validated {package_file}")

    logger.info(f"Validated {valid} packages")
    logger.info(f"Found {corrupted} corrupted packages")


if __name__ == "__main__":
    main()
