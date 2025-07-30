from yta_validation import PythonValidator

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
        name: str
    ):
        """
        Try to install the dependency with the
        given 'name' using pip.
        """
        return subprocess.check_call([sys.executable, '-m', 'pip', 'install', name])

    @staticmethod
    def uninstall(
        name: str
    ):
        """
        Try to uninstall the dependency with the
        given 'name' using pip.
        """
        return subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', name])