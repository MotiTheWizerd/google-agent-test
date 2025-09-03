"""Debug script to check Mem0 client method signatures."""

import sys
import os
from dotenv import load_dotenv
import inspect

# Load environment variables
load_dotenv()

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mem0 import MemoryClient

# Check what methods are available and their signatures
api_key = os.getenv("MEM0_API_KEY", "")
if not api_key:
    print("ERROR: MEM0_API_KEY not found in environment")
    exit(1)
    
client = MemoryClient(api_key=api_key)

print("MemoryClient.add signature:")
print(inspect.signature(client.add))

print("\nMemoryClient.search signature:")
print(inspect.signature(client.search))

print("\nMemoryClient.delete signature:")
print(inspect.signature(client.delete))