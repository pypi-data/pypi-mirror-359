from yta_validation import PythonValidator
from yta_validation.parameter import ParameterValidator
from yta_file.handler import FileHandler
from yta_temp import Temp
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
    ) -> bool:
        """
        Check if the dependency with the given
        'name' is installed or not.
        """
        return PythonValidator.is_dependency_installed(name)

    @staticmethod
    def install(
        name: str,
        version_range: Union[str, None] = None
    ) -> int:
        """
        Try to install the dependency with the
        given 'name' using pip. It will use the
        'version_range' specificator if provided,
        that must be something like 
        ">=2.0.0,<3.0.0".

        Command used:
        - `pip install -y {name}{version_range}`
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
    ) -> int:
        """
        Try to uninstall the dependency with the
        given 'name'.

        Command used:
        - `pip uninstall -y {name}`
        """
        ParameterValidator.validate_mandatory_string('name', name, do_accept_empty = False)

        return subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', name])

    @staticmethod
    def create_backup() -> str:
        """
        Create a backup with the current status of
        the project, containing all the dependencies
        and their versions, to be able to install it
        again, and return the absolute path to the
        backup file that has been written.

        Command used:
        - `pip freeze`
        """
        # TODO: Careful, we have an issue with the 
        # WIP_FOLDER and this is returning an absolute
        # path...
        filename = Temp.get_wip_filename('pip_backup.txt')

        # Using 'pip freeze > {filename}' is not
        # possible as a subprocess
        return FileHandler.write_str(
            filename,
            subprocess.check_output([sys.executable, '-m', 'pip', 'freeze', '>', filename]).decode('utf-8')
        )
    
    @staticmethod
    def restore_backup(
        filename: str
    ) -> int:
        """
        Restore a backup and reinstall all the
        dependencies with the version that was
        written in the backup file with the
        'filename' given.

        Command used:
        - `pip install --force-reinstall -r {filename}`
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        # TODO: This is too slow, I think it is
        # reinstalling all the packages not only
        # the differents...
        return subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--force-reinstall', '-r', filename])

