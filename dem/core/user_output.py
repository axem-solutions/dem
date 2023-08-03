"""The core can provide information through this module to the user."""
# dem/core/user_output.py

from abc import ABC, abstractmethod
from typing import Generator

class UserOutput(ABC):
    @abstractmethod
    def msg(self, text: str, is_title: bool = False) -> None:
        pass

    @abstractmethod
    def get_confirm(self, text: str, confirm_text: str) -> None:
        pass

    @abstractmethod
    def progress_generator(self, generator: Generator) -> None:
        pass

    @abstractmethod
    def status_generator(self, generator: Generator) -> None:
        pass

class NoUserOutput(UserOutput):
    def msg(self, text: str, is_title: bool = False) -> None:
        pass

    def get_confirm(self, text: str, confirm_text: str) -> None:
        pass

    def progress_generator(self, generator: Generator) -> None:
        for _ in generator:
            pass

    def status_generator(self, generator: Generator) -> None:
        for _ in generator:
            pass