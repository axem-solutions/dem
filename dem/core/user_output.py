"""The core can provide information through this module to the user."""
# dem/core/user_output.py

from abc import ABC, abstractmethod
from typing import Generator

class UserOutput(ABC):
    """ Abstract base class for the user output. Acts as an interface between the core modules and 
        the UI.
    """
    @abstractmethod
    def msg(self, text: str, is_title: bool = False) -> None:
        """ Send a message.
        
            Args:
                text -- the text to print
                is_title -- the text is the title of a new section.
        """
        pass

    @abstractmethod
    def error(self, text: str) -> None:
        """ Send and error message
        
            Args:
                text -- the error message
        """
        pass

    @abstractmethod
    def get_confirm(self, text: str, confirm_text: str) -> None:
        """ Get confirmation from the user.
        
            Args:
                text -- message to print (can be empty)
                confirm_text: the action the user needs to confirm
        """
        pass

    @abstractmethod
    def progress_generator(self, generator: Generator) -> None:
        """ Process the progress generator. 

            The input generator must be exhausted.

            Args:
                generator -- the generator
        """
        pass

    @abstractmethod
    def status_generator(self, generator: Generator) -> None:
        """ Process the status generator. 

            The input generator must be exhausted.

            Args:
                generator -- the generator
        """
        pass

class NoUserOutput(UserOutput):
    """ This class is assigned to the interface when no UI is present. The methods don't do anything
        except exhausting the generator if applicable.
    """
    def msg(self, text: str, is_title: bool = False) -> None:
        pass

    def error(self, text: str) -> None:
        pass

    def get_confirm(self, text: str, confirm_text: str) -> None:
        pass

    def progress_generator(self, generator: Generator) -> None:
        for _ in generator:
            pass

    def status_generator(self, generator: Generator) -> None:
        for _ in generator:
            pass