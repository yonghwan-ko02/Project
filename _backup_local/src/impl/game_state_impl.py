from typing import Dict, Any
from src.core.game_state import GameState, EndingType

class GameStateImpl(GameState):
    """
    Implementation of GameState for tracking player choices and story progression.
    """
    
    def __init__(self):
        self.choices: Dict[str, Any] = {}
        # Define key decision points that affect the ending
        self.reboot_indicators = [
            "refused_impossible_task",
            "rejected_toad_help",
            "skipped_festival",
            "refused_marriage",
            "confronted_stepmother",
            "helped_patjwi",
            "helped_patjwi",
            "left_home_early"
        ]
        self.scene_state = {
            "chapter": "chapter_1_house",
            "status": "unresolved"
        }
    
    def record_choice(self, choice_key: str, choice_value: Any) -> None:
        """Records a player's choice."""
        self.choices[choice_key] = choice_value
        print(f"[GameState] Recorded choice: {choice_key} = {choice_value}")
    
    def get_choice(self, choice_key: str) -> Any:
        """Retrieves a previously recorded choice."""
        return self.choices.get(choice_key, None)
    
    def get_all_choices(self) -> Dict[str, Any]:
        """Returns all recorded choices."""
        return self.choices.copy()
    
    def determine_ending(self) -> EndingType:
        """
        Determines the ending type based on accumulated choices.
        
        Logic:
        - If reboot_score >= 60: REBOOT ending (significantly deviated)
        - If reboot_score <= 20: ORIGINAL ending (mostly followed original)
        - Otherwise: NEUTRAL (mixed path)
        """
        score = self.get_reboot_score()
        
        if score >= 60:
            return EndingType.REBOOT
        elif score <= 20:
            return EndingType.ORIGINAL
        else:
            return EndingType.NEUTRAL
    
    def get_reboot_score(self) -> int:
        """
        Calculates how much the player has deviated from the original story.
        
        Returns:
            int: Score from 0 (completely original) to 100 (completely reboot)
        """
        if not self.choices:
            return 0
        
        reboot_count = 0
        for indicator in self.reboot_indicators:
            if self.choices.get(indicator, False):
                reboot_count += 1
        
        # Calculate percentage
        max_reboot_choices = len(self.reboot_indicators)
        if max_reboot_choices == 0:
            return 0
            
        score = int((reboot_count / max_reboot_choices) * 100)
        return score
    
    def get_state_summary(self) -> str:
        """
        Returns a human-readable summary of the current game state.
        
        Returns:
            str: Summary of choices and current trajectory
        """
        ending = self.determine_ending()
        score = self.get_reboot_score()
        
        summary = f"현재 챕터: {self.scene_state['chapter']} ({self.scene_state['status']})\n"
        summary += f"현재 리부트 점수: {score}/100\n"
        summary += f"예상 엔딩: {ending.value}\n"
        summary += f"주요 선택 내역:\n"
        
        for key, value in self.choices.items():
            summary += f"  - {key}: {value}\n"
        
        return summary

    def update_scene(self, chapter: str, status: str) -> None:
        """Updates the current scene state."""
        self.scene_state["chapter"] = chapter
        self.scene_state["status"] = status
        print(f"[GameState] Scene updated: {chapter} ({status})")

    def get_scene(self) -> Dict[str, str]:
        """Returns the current scene state."""
        return self.scene_state.copy()
