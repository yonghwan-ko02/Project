import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.lore_keeper import LoreKeeper

# We will test the implementation, assuming it will be in src.impl.lore_keeper_impl
# Since it doesn't exist yet, we can't import it at top level if we want to run this *partial* test without erroring on import.
# But for TDD, strict TDD says write test, it fails (ImportError).

class TestLoreKeeperImpl(unittest.TestCase):
    def setUp(self):
        # Import inside setup specifically for TDD flow if we were running piece by piece, 
        # but here we will write the file next.
        from src.impl.lore_keeper_impl import LoreKeeperImpl
        self.impl_class = LoreKeeperImpl

    def test_inheritance(self):
        """Verify LoreKeeperImpl implements LoreKeeper interface"""
        keeper = self.impl_class()
        self.assertIsInstance(keeper, LoreKeeper)

    @patch('src.impl.lore_keeper_impl.Chroma')
    @patch('src.impl.lore_keeper_impl.OllamaEmbeddings')
    def test_build_index(self, mock_embeddings, mock_chroma):
        """Test building index calls ChromaDB with documents"""
        keeper = self.impl_class()
        
        # Mock documents
        keeper.documents = [MagicMock(), MagicMock()] 
        
        keeper.build_index()
        
        # Verify Chroma.from_documents is called
        mock_chroma.from_documents.assert_called_once()

    @patch('builtins.open', new_callable=mock_open, read_data="Test story content")
    @patch('src.impl.lore_keeper_impl.RecursiveCharacterTextSplitter')
    def test_load_book(self, mock_splitter, mock_file):
        """Test loading book reads file and splits text"""
        keeper = self.impl_class()
        
        # Setup mock splitter return
        mock_splitter_instance = mock_splitter.return_value
        mock_splitter_instance.split_text.return_value = ["chunk1", "chunk2"]
        mock_splitter_instance.create_documents.return_value = ["doc1", "doc2"]
        
        keeper.load_book("dummy_path.txt")
        
        # Verify file opened
        open.assert_called_with("dummy_path.txt", 'r', encoding='utf-8')
        # Verify split called
        mock_splitter_instance.create_documents.assert_called()
        self.assertEqual(len(keeper.documents), 2)

if __name__ == '__main__':
    unittest.main()
