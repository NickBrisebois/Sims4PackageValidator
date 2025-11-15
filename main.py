from argparse import ArgumentParser
from pathlib import Path

from files import CCType, find_cc_files, write_file_to_output
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
    file_stats: dict[CCType, int] = {t: 0 for t in CCType}

    validator_map = {
        CCType.PACKAGE: package_validator,
        CCType.SCRIPT: ts4cript_validator,
    }

    for cc_file in find_cc_files(args.directory):
        file_stats[cc_file.file_type] += 1
        validator = validator_map.get(cc_file.file_type)
        if validator and (error := validator.validate(cc_file)):
            logger.error(f"Validation error for {cc_file.file_name}: {error}")
            validity_stats["corrupted"] += 1
            continue
        else:
            validity_stats["valid"] += 1
            logger.info(f"Validated {cc_file.file_name}")
            # write_file_to_output(package_file, args.outdir)

    logger.info(f"Validated {validity_stats['valid']} cc files")
    logger.info(f"Found {validity_stats['corrupted']} corrupted cc files")
    logger.info(f"Found {file_stats[CCType.SCRIPT]} TS4Script files")
    logger.info(f"Found {file_stats[CCType.PACKAGE]} SimsPackage files")
    logger.info(f"Found {file_stats[CCType.IMAGE]} image files")
    logger.info(f"Found {file_stats[CCType.OTHER]} other files")


if __name__ == "__main__":
    main()
