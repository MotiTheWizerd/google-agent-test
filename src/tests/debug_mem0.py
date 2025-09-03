"""Debug script to check Mem0 client methods."""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mem0 import MemoryClient

# Check what methods are available
print("MemoryClient methods:")
api_key = os.getenv("MEM0_API_KEY", "")
if not api_key:
    print("ERROR: MEM0_API_KEY not found in environment")
    exit(1)
    
client = MemoryClient(api_key=api_key)
for attr in dir(client):
    if not attr.startswith('_'):
        print(f"  {attr}")

print("\nMemoryClient attributes:")
print([attr for attr in dir(client) if not attr.startswith('_')])