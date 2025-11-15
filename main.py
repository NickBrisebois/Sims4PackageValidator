from argparse import ArgumentParser
from pathlib import Path

from files import CCType, find_package_files
from log_handler import LogHandler
from validators.package_validator import SimsPackageValidator
from validators.ts4script_validator import TS4ScriptValidator


def main():
    # for root, subdirs, files in os.walk()
    parser = ArgumentParser(description="Package Checker")
    parser.add_argument("-d", "--directory", type=Path, help="Directory to check")
    parser.add_argument("-o", "--outdir", type=Path, help="Output directory")
    args = parser.parse_args()

    logger = LogHandler.get_logger(__name__)
    package_validator = SimsPackageValidator(logger)
    ts4cript_validator = TS4ScriptValidator(logger)

    validity_stats = {"corrupted": 0, "valid": 0}
    file_stats = {CCType.SCRIPT: 0, CCType.PACKAGE: 0, CCType.IMAGE: 0}

    validator_map = {
        CCType.PACKAGE: package_validator,
        CCType.SCRIPT: ts4cript_validator,
    }

    for package_file in find_package_files(args.directory):
        file_stats[package_file.file_type] += 1
        validator = validator_map.get(package_file.file_type)
        if validator and (error := validator.validate(package_file)):
            logger.error(f"Validation error for {package_file.file_name}: {error}")
            validity_stats["corrupted"] += 1
            continue
        else:
            validity_stats["valid"] += 1
            logger.info(f"Validated {package_file.file_name}")

    logger.info(f"Validated {validity_stats['valid']} packages")
    logger.info(f"Found {validity_stats['corrupted']} corrupted packages")
    logger.info(f"Found {file_stats[CCType.SCRIPT]} TS4Script files")
    logger.info(f"Found {file_stats[CCType.PACKAGE]} SimsPackage files")
    logger.info(f"Found {file_stats[CCType.IMAGE]} image files")


if __name__ == "__main__":
    main()
