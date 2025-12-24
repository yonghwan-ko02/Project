
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.impl.lore_keeper_impl import LoreKeeperImpl

def test_retrieval():
    lore_keeper = LoreKeeperImpl()
    story_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'story.txt')
    
    print(f"Loading story from {story_path}...")
    lore_keeper.load_book(story_path)
    lore_keeper.build_index()
    
    queries = ["시작", "콩쥐의 등장", "옛날 옛적에", "Chapter 1"]
    
    print("\n=== Retrieval Test ===")
    for q in queries:
        print(f"\nQuery: {q}")
        results = lore_keeper.retrieve(q, top_k=1)
        if results:
            print(f"Result (First 100 chars): {results[0][:100]}...")
        else:
            print("No results found.")

if __name__ == "__main__":
    test_retrieval()
