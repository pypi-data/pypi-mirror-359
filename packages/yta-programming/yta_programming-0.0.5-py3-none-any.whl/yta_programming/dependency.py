from yta_validation import PythonValidator
from yta_validation.parameter import ParameterValidator
from typing import Union

import subprocess
import sys


class Dependency:
    """
    Class to wrap functionality related to
    managing dependencies.
    """

    @staticmethod
    def is_installed(
        name: str
    ):
        """
        Check if the dependency with the given
        'name' is installed or not.
        """
        return PythonValidator.is_dependency_installed(name)

    @staticmethod
    def install(
        name: str,
        version_range: Union[str, None] = None
    ):
        """
        Try to install the dependency with the
        given 'name' using pip. It will use the
        'version_range' specificator if provided,
        that must be something like 
        ">=2.0.0,<3.0.0".
        """
        ParameterValidator.validate_mandatory_string('name', name, do_accept_empty = False)
        ParameterValidator.validate_string('version_range', version_range, do_accept_empty = False)

        name = (
             f'{name}{version_range}'
             if version_range is not None else
             name
        )

        return subprocess.check_call([sys.executable, '-m', 'pip', 'install', name])

    @staticmethod
    def uninstall(
        name: str
    ):
        """
        Try to uninstall the dependency with the
        given 'name' using pip.
        """
        ParameterValidator.validate_mandatory_string('name', name, do_accept_empty = False)

        return subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', name])