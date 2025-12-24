import unittest
from unittest.mock import MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.io import InputProvider, OutputDisplay
from src.core.lore_keeper import LoreKeeper
from src.core.dungeon_master import DungeonMaster
from src.core.game_state import GameState

class TestGameLoop(unittest.TestCase):
    def setUp(self):
        try:
            from src.impl.game_loop import GameLoop
            self.loop_class = GameLoop
        except ImportError:
            self.fail("GameLoop module not found")
            
        self.mock_input = MagicMock(spec=InputProvider)
        self.mock_output = MagicMock(spec=OutputDisplay)
        self.mock_lore = MagicMock(spec=LoreKeeper)
        self.mock_dm = MagicMock()  # Use MagicMock without spec for flexibility
        self.mock_game_state = MagicMock(spec=GameState)
        
        # Add persona-related methods to mock
        self.mock_dm.get_persona_description.return_value = "Classic persona"
        self.mock_dm.get_current_persona.return_value = "classic"
        self.mock_dm.list_available_personas.return_value = ["classic", "dialect", "cynical", "modern", "poetic"]
        
        self.game = self.loop_class(
            input_provider=self.mock_input,
            output_display=self.mock_output,
            lore_keeper=self.mock_lore,
            dungeon_master=self.mock_dm,
            game_state=self.mock_game_state
        )

    def test_run_single_turn(self):
        """Test a single turn of the game loop"""
        # Setup mocks
        self.mock_input.get_input.side_effect = ["Hello", "quit"] # First input then quit
        self.mock_lore.retrieve.return_value = ["Context"]
        self.mock_dm.generate_story.return_value = "AI Response"
        
        # Run loop
        self.game.run()
        
        # Verify interactions
        self.mock_input.get_input.assert_called()
        self.mock_lore.retrieve.assert_called_with("Hello")
        self.mock_dm.generate_story.assert_called_with("Hello", ["Context"])
        self.mock_output.display.assert_called_with("AI Response")

    def test_memory_management(self):
        """Test if memory/history is maintained (simplified for MVP)"""
        # MVP: Just check if history buffer is updated
        self.mock_input.get_input.side_effect = ["Action 1", "quit"]
        self.mock_dm.generate_story.return_value = "Result 1"
        
        self.game.run()
        
        self.assertEqual(len(self.game.history), 1)
        self.assertEqual(self.game.history[0]['user'], "Action 1")
        self.assertEqual(self.game.history[0]['ai'], "Result 1")

if __name__ == '__main__':
    unittest.main()
