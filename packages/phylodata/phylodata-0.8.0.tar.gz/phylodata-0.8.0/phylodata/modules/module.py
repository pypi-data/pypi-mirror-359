from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Module(ABC, Generic[T]):
    @abstractmethod
    def ui(self):
        """Renders the streamlit UI."""
        pass

    @abstractmethod
    def validate(self):
        """Validates the input. Throws a ValidationError with a
        message if the input is invalid."""
        pass

    @abstractmethod
    def parse(self) -> T:
        """Parses the input and returns a valid object. Throws a ValidationError
        with a message if parsing fails."""
        pass
