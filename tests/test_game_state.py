import unittest
from unittest.mock import MagicMock
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.game_state import GameState, EndingType
from src.impl.game_state_impl import GameStateImpl

class TestGameStateImpl(unittest.TestCase):
    def setUp(self):
        self.game_state = GameStateImpl()
    
    def test_inheritance(self):
        """Verify GameStateImpl implements GameState interface"""
        self.assertIsInstance(self.game_state, GameState)
    
    def test_record_and_get_choice(self):
        """Test recording and retrieving choices"""
        self.game_state.record_choice("helped_toad", True)
        self.assertEqual(self.game_state.get_choice("helped_toad"), True)
        
        self.game_state.record_choice("refused_impossible_task", False)
        self.assertEqual(self.game_state.get_choice("refused_impossible_task"), False)
    
    def test_get_nonexistent_choice(self):
        """Test retrieving a choice that doesn't exist"""
        result = self.game_state.get_choice("nonexistent_choice")
        self.assertIsNone(result)
    
    def test_get_all_choices(self):
        """Test retrieving all choices"""
        self.game_state.record_choice("choice1", "value1")
        self.game_state.record_choice("choice2", "value2")
        
        all_choices = self.game_state.get_all_choices()
        self.assertEqual(len(all_choices), 2)
        self.assertEqual(all_choices["choice1"], "value1")
        self.assertEqual(all_choices["choice2"], "value2")
    
    def test_reboot_score_no_choices(self):
        """Test reboot score with no choices made"""
        score = self.game_state.get_reboot_score()
        self.assertEqual(score, 0)
    
    def test_reboot_score_all_original(self):
        """Test reboot score when following original story"""
        # All reboot indicators are False
        self.game_state.record_choice("refused_impossible_task", False)
        self.game_state.record_choice("rejected_toad_help", False)
        self.game_state.record_choice("skipped_festival", False)
        
        score = self.game_state.get_reboot_score()
        self.assertEqual(score, 0)
    
    def test_reboot_score_partial_reboot(self):
        """Test reboot score with some deviations"""
        # 2 out of 7 reboot indicators are True
        self.game_state.record_choice("refused_impossible_task", True)
        self.game_state.record_choice("rejected_toad_help", True)
        
        score = self.game_state.get_reboot_score()
        # 2/7 * 100 = ~28
        self.assertGreater(score, 20)
        self.assertLess(score, 35)
    
    def test_reboot_score_full_reboot(self):
        """Test reboot score when completely deviating from original"""
        # All reboot indicators are True
        for indicator in self.game_state.reboot_indicators:
            self.game_state.record_choice(indicator, True)
        
        score = self.game_state.get_reboot_score()
        self.assertEqual(score, 100)
    
    def test_determine_ending_original(self):
        """Test ending determination for original path"""
        # No reboot choices
        ending = self.game_state.determine_ending()
        self.assertEqual(ending, EndingType.ORIGINAL)
    
    def test_determine_ending_reboot(self):
        """Test ending determination for reboot path"""
        # Most reboot indicators are True (5 out of 7)
        self.game_state.record_choice("refused_impossible_task", True)
        self.game_state.record_choice("rejected_toad_help", True)
        self.game_state.record_choice("skipped_festival", True)
        self.game_state.record_choice("refused_marriage", True)
        self.game_state.record_choice("confronted_stepmother", True)
        
        ending = self.game_state.determine_ending()
        self.assertEqual(ending, EndingType.REBOOT)
    
    def test_determine_ending_neutral(self):
        """Test ending determination for neutral/mixed path"""
        # Some reboot choices (2 out of 7, ~28%)
        self.game_state.record_choice("refused_impossible_task", True)
        self.game_state.record_choice("helped_patjwi", True)
        
        ending = self.game_state.determine_ending()
        self.assertEqual(ending, EndingType.NEUTRAL)
    
    def test_state_summary(self):
        """Test state summary generation"""
        self.game_state.record_choice("helped_toad", True)
        summary = self.game_state.get_state_summary()
        
        self.assertIn("리부트 점수", summary)
        self.assertIn("예상 엔딩", summary)
        self.assertIn("helped_toad", summary)

if __name__ == '__main__':
    unittest.main()
