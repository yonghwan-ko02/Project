from abc import ABC, abstractmethod

class InputProvider(ABC):
    @abstractmethod
    def get_input(self, prompt: str = "") -> str:
        """Get input from user."""
        pass

class OutputDisplay(ABC):
    @abstractmethod
    def display(self, message: str) -> None:
        """Display message to user."""
        pass
        
    @abstractmethod
    def display_system(self, message: str) -> None:
        """Display system message (different style)."""
        pass
