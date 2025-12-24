from abc import ABC, abstractmethod
from typing import Dict, List, Any
from enum import Enum

class EndingType(Enum):
    """Enum for different ending types"""
    ORIGINAL = "original"  # Following the original story
    REBOOT = "reboot"      # Alternative story path
    NEUTRAL = "neutral"    # Undecided yet

class GameState(ABC):
    """
    Abstract Base Class for GameState.
    Tracks player choices and determines story branching.
    """
    
    @abstractmethod
    def record_choice(self, choice_key: str, choice_value: Any) -> None:
        """
        Records a player's choice.
        
        Args:
            choice_key (str): The identifier for the choice (e.g., "helped_toad")
            choice_value (Any): The value of the choice (e.g., True, False, or custom string)
        """
        pass
    
    @abstractmethod
    def get_choice(self, choice_key: str) -> Any:
        """
        Retrieves a previously recorded choice.
        
        Args:
            choice_key (str): The identifier for the choice
            
        Returns:
            Any: The value of the choice, or None if not found
        """
        pass
    
    @abstractmethod
    def get_all_choices(self) -> Dict[str, Any]:
        """
        Returns all recorded choices.
        
        Returns:
            Dict[str, Any]: Dictionary of all choices
        """
        pass
    
    @abstractmethod
    def determine_ending(self) -> EndingType:
        """
        Determines the ending type based on accumulated choices.
        
        Returns:
            EndingType: The type of ending (ORIGINAL, REBOOT, or NEUTRAL)
        """
        pass
    
    @abstractmethod
    def get_reboot_score(self) -> int:
        """
        Calculates how much the player has deviated from the original story.
        
        Returns:
            int: Score from 0 (completely original) to 100 (completely reboot)
        """
        pass
