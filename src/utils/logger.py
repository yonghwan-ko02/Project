import json
import os
from datetime import datetime
from typing import Dict, Any

class Logger:
    """
    Singleton logger for game sessions.
    Saves user input/AI response pairs to JSONL format.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.log_dir = "logs"
        self.session_file = None
        self._initialized = True
        self._create_log_directory()
        self._create_session_file()
    
    def _create_log_directory(self):
        """Create logs directory if it doesn't exist"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _create_session_file(self):
        """Create a new session log file with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = os.path.join(self.log_dir, f"session_{timestamp}.jsonl")
    
    def log_turn(self, user_input: str, ai_response: str, metadata: Dict[str, Any] = None):
        """
        Log a single turn (user input + AI response) to JSONL file.
        
        Args:
            user_input: The user's input
            ai_response: The AI's response
            metadata: Optional metadata (e.g., game state, timestamp)
        """
        if not self.session_file:
            self._create_session_file()
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response": ai_response,
            "metadata": metadata or {}
        }
        
        try:
            with open(self.session_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Warning: Failed to write log: {e}")
    
    def get_session_file(self) -> str:
        """Returns the current session file path"""
        return self.session_file
    
    def load_session(self, session_file: str) -> list:
        """
        Load a previous session from JSONL file.
        
        Args:
            session_file: Path to the session file
            
        Returns:
            List of log entries
        """
        entries = []
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                for line in f:
                    entries.append(json.loads(line))
        except Exception as e:
            print(f"Error loading session: {e}")
        
        return entries
