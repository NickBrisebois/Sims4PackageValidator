import abc

from files import PackageFile


class BaseValidator(abc.ABC):
    def validate(self, package_file: PackageFile):
        raise NotImplementedError("Subclasses must implement validate method")
