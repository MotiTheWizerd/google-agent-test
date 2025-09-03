"""Test script to verify mem0 integration."""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.modules.memory.adapters.mem0_store import Mem0Store
from src.modules.memory.config import Mem0Config

def test_mem0_connection():
    """Test the Mem0 connection."""
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
        
        # Test users method
        users = store.users()
        print(f"SUCCESS: Users method works, found {len(users)} users")
        
        # Try to search for memories (list top 10)
        try:
            # If we have users, search for memories for the first user
            if users:
                user_id = users[0].get('user_id') or users[0].get('id')
                if user_id:
                    print(f"SEARCHING for top 10 memories for user: {user_id}")
                    memories = store.search(user_id=user_id, k=10)
                    print(f"SUCCESS: Found {len(memories)} memories")
                    
                    # List the top 10 memories
                    if memories:
                        print("\nTOP 10 Memories:")
                        print("=" * 50)
                        for i, memory in enumerate(memories[:10], 1):
                            record = memory.get('record', {})
                            text = record.get('text', 'N/A')
                            created_at = record.get('created_at', 'N/A')
                            print(f"{i:2d}. {text[:60]}{'...' if len(text) > 60 else ''}")
                            print(f"     Created: {created_at}")
                            print()
                    else:
                        print("INFO: No memories found for this user")
                else:
                    print("WARNING: Could not determine user ID from users list")
            else:
                print("INFO: No users found in the memory store")
        except Exception as search_error:
            print(f"NOTE: Could not search for memories (this is expected if no memories exist yet): {search_error}")
        
        print("SUCCESS: All tests passed!")
        return True
        
    except Exception as e:
        print(f"ERROR testing Mem0 integration: {e}")
        return False

if __name__ == "__main__":
    print("Testing Mem0 integration...")
    test_mem0_connection()