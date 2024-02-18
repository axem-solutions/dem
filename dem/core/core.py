"""All core module must inherit from the Core class."""
# dem/core/core.py

from dem.core.user_output import UserOutput, NoUserOutput
from dem.core.data_management import ConfigFile

class Core():
    """ Base class for all core classes.
    
        Class attributes:
            user_output -- interface to the UI (must be a descendant of the UserOutput class)
    """
    user_output: UserOutput = NoUserOutput()
    config_file: ConfigFile = ConfigFile()

    """ Set the user output class for all core descendant core classes.
    
        Args:
            user_output -- interface to the UI (must be a descendant of the UserOutput class)
    """
    @classmethod
    def set_user_output(cls, user_output: UserOutput) -> None:
        cls.user_output = user_output