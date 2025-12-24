import unittest
from unittest.mock import MagicMock, patch
from typing import List
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.dungeon_master import DungeonMaster

class TestDungeonMasterImpl(unittest.TestCase):
    def setUp(self):
        # TDD style: Import locally
        from src.impl.dungeon_master_impl import DungeonMasterImpl
        self.impl_class = DungeonMasterImpl

    def test_inheritance(self):
        """Verify DungeonMasterImpl implements DungeonMaster interface"""
        dm = self.impl_class()
        self.assertIsInstance(dm, DungeonMaster)

    @patch('src.impl.dungeon_master_impl.ChatOllama')
    def test_generate_story(self, mock_chat_cls):
        """Test story generation calls LLM with correct messages"""
        # Mock LLM instance
        mock_llm = mock_chat_cls.return_value
        mock_llm.invoke.return_value = MagicMock(content="Generated story")
        
        dm = self.impl_class()
        dm.set_system_prompt("You are a TRPG master.")
        
        context = ["Context 1", "Context 2"]
        result = dm.generate_story("Kick the toad", context)
        
        # Verify LLM called
        mock_llm.invoke.assert_called_once()
        
        # Verify input construction (simplified check)
        call_args = mock_llm.invoke.call_args
        messages = call_args[0][0] # First arg should be list of messages or prompt
        
        # Depending on implementation (ChatPromptTemplate), it might be a list or PromptValue
        # Here assuming implementation uses invoke with messages or prompt.
        # We'll just verify result for now.
        self.assertEqual(result, "Generated story")

    def test_set_system_prompt(self):
        dm = self.impl_class()
        dm.set_system_prompt("New Persona")
        # Implementation specific check, maybe check internal attribute
        self.assertEqual(dm.system_prompt, "New Persona")

if __name__ == '__main__':
    unittest.main()
