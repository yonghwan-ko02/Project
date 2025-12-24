from abc import ABC, abstractmethod
from typing import List

class DungeonMaster(ABC):
    """
    Abstract Base Class for DungeonMaster.
    Responsible for generating story content using AI.
    """
    
    @abstractmethod
    def set_system_prompt(self, prompt: str) -> None:
        """
        Sets the system prompt (persona) for the AI.
        
        Args:
            prompt (str): The system prompt.
        """
        pass

    @abstractmethod
    def generate_story(self, user_input: str, context: List[str]) -> str:
        """
        Generates the next part of the story based on user input and retrieved context.
        
        Args:
            user_input (str): The user's action or dialogue.
            context (List[str]): Relevant context chunks retrieved from LoreKeeper.
            
        Returns:
            str: The generated story text.
        """
        pass
