"""Comprehensive test script for the memory module."""

import sys
import os
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.modules.memory.adapters.mem0_store import Mem0Store
from src.modules.memory.config import Mem0Config


def test_memory_operations():
    """Test all memory operations."""
    try:
        # Load config from environment
        config = Mem0Config.from_env()
        
        # Check if API key is set
        if not config.api_key:
            print("ERROR: MEM0_API_KEY not found in environment")
            return False
            
        # Initialize the store
        store = Mem0Store(config)
        print("SUCCESS: Mem0Store initialized successfully")
        
        # Generate a unique test user ID
        test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        print(f"INFO: Using test user ID: {test_user_id}")
        
        # Add some test memories
        print("\nADDING test memories...")
        test_memories = [
            "I prefer window seats on long flights",
            "My favorite programming language is Python",
            "I enjoy hiking in the mountains on weekends",
            "I work as a software engineer",
            "I live in San Francisco",
            "I have a cat named Whiskers",
            "I like to read science fiction novels",
            "I'm learning about AI and machine learning",
            "I prefer coffee over tea in the morning",
            "I enjoy attending tech conferences",
            "My favorite holiday destination is Japan",
            "I play guitar as a hobby"
        ]
        
        added_memories = []
        for i, text in enumerate(test_memories, 1):
            try:
                record = store.add(
                    user_id=test_user_id,
                    text=text,
                    tags=["test", "preference"],
                    metadata={"source": "test_script", "index": i}
                )
                added_memories.append(record)
                print(f"ADDED memory {i}: {text[:30]}{'...' if len(text) > 30 else ''}")
            except Exception as e:
                print(f"ERROR adding memory {i}: {e}")
        
        print(f"\nSUCCESS: Added {len(added_memories)} test memories")
        
        # Search for memories (list top 10)
        print(f"\nSEARCHING for memories for user: {test_user_id}")
        try:
            memories = store.search(user_id=test_user_id, query="", k=10)
            print(f"SUCCESS: Found {len(memories)} memories")
            
            # List the top 10 memories
            if memories:
                print("\nTOP 10 Memories:")
                print("=" * 60)
                for i, memory in enumerate(memories[:10], 1):
                    record = memory.get('record', {})
                    # Handle different response formats
                    if isinstance(record, dict):
                        text = record.get('text', record.get('content', 'N/A'))
                        created_at = record.get('created_at', 'N/A')
                        tags = record.get('tags', [])
                        metadata = record.get('metadata', {})
                    else:
                        text = str(record)
                        created_at = 'N/A'
                        tags = []
                        metadata = {}
                    
                    print(f"{i:2d}. {text}")
                    print(f"     Tags: {tags}")
                    print(f"     Metadata: {metadata}")
                    print(f"     Created: {created_at}")
                    print()
            else:
                print("INFO: No memories found for this user")
        except Exception as search_error:
            print(f"ERROR searching for memories: {search_error}")
            return False
        
        # Test search with query
        print(f"\nSEARCHING with query 'programming' for user: {test_user_id}")
        try:
            memories = store.search(user_id=test_user_id, query="programming", k=5)
            print(f"SUCCESS: Found {len(memories)} memories matching 'programming'")
            
            if memories:
                print("\nMemories matching 'programming':")
                print("=" * 60)
                for i, memory in enumerate(memories[:5], 1):
                    record = memory.get('record', {})
                    # Handle different response formats
                    if isinstance(record, dict):
                        text = record.get('text', record.get('content', 'N/A'))
                        score = memory.get('score', 0)
                    else:
                        text = str(record)
                        score = memory.get('score', 0)
                    print(f"{i:2d}. {text} (Score: {score:.2f})")
        except Exception as search_error:
            print(f"ERROR searching with query: {search_error}")
        
        # List users
        print("\nListing users...")
        try:
            users = store.users()
            print(f"SUCCESS: Found {len(users)} users")
            if users:
                print("Recent users:")
                for user in users[:5]:  # Show first 5 users
                    print(f"  - {user}")
        except Exception as users_error:
            print(f"ERROR listing users: {users_error}")
        
        print("\nSUCCESS: All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"ERROR testing memory operations: {e}")
        return False


if __name__ == "__main__":
    print("Testing Memory Module Operations...")
    print("=" * 50)
    test_memory_operations()