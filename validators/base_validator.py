import abc

from files import CCFile


class BaseValidator(abc.ABC):
    def validate(self, package_file: CCFile):
        raise NotImplementedError("Subclasses must implement validate method")
