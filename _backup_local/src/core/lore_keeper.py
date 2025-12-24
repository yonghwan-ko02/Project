from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LoreKeeper(ABC):
    """
    Abstract Base Class for LoreKeeper.
    Responsible for loading data, building index, and retrieving context.
    """
    
    @abstractmethod
    def load_book(self, file_path: str) -> None:
        """
        Loads the text file and prepares it for indexing (e.g., chunking).
        
        Args:
            file_path (str): The absolute path to the text file.
        """
        pass

    @abstractmethod
    def build_index(self) -> None:
        """
        Builds or loads the vector index from the loaded text.
        """
        pass

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieves relevant context chunks based on the user query.
        
        Args:
            query (str): The search query.
            top_k (int): Number of relevant documents to return.
            
        Returns:
            List[str]: A list of relevant text chunks.
        """
        pass
