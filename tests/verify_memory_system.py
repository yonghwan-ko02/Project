import sys
import os
from typing import List
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Force UTF-8 for Windows console
sys.stdout.reconfigure(encoding='utf-8')

from src.impl.dungeon_master_impl import DungeonMasterImpl

class MockLLMResponse:
    def __init__(self, content):
        self.content = content

class MockLLM:
    def invoke(self, messages):
        # Return a fake summary
        return MockLLMResponse("요약됨: 콩쥐는 독에 물 붓기를 포기하고 두꺼비와 협상했습니다.")

def test_memory_summarization():
    print("[Test] Initializing DungeonMaster...")
    dm = DungeonMasterImpl(model_name="mock-model", persona_type="radical")
    
    # Mock the LLM to avoid actual API calls/Ollama delays
    dm.llm = MockLLM()
    
    # Cheat: Inject fake conversation history (6 turns)
    print("[Test] Injecting 6 turns of conversation...")
    for i in range(6):
        dm.conversation_history.append({
            "user": f"Turn {i} User Choice",
            "ai": f"Turn {i} AI Response"
        })
    
    print(f"[Before] History Length: {len(dm.conversation_history)}")
    print(f"[Before] Long-term Memory: {dm.long_term_memory}")
    
    # Force summarization trigger
    # In actual class, this happens inside generate_story, but we call internal method to test logic
    print("[Test] Triggering _summarize_old_memories()...")
    dm._summarize_old_memories()
    
    print(f"[After] History Length: {len(dm.conversation_history)}")
    print(f"[After] Long-term Memory: {dm.long_term_memory}")
    
    # Verification
    if len(dm.conversation_history) == 4:
        print("[PASS] History truncated correctly (6 -> 4).")
    else:
        print(f"[FAIL] History length incorrect: {len(dm.conversation_history)}")
        
    if "요약됨" in dm.long_term_memory:
        print("[PASS] Long-term memory updated.")
    else:
        print("[FAIL] Long-term memory not updated.")

if __name__ == "__main__":
    test_memory_summarization()
