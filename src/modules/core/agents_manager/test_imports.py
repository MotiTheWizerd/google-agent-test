"""Test file to verify the agents manager module imports work correctly."""

import asyncio
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Test importing from the agents_manager module
try:
    from modules.core.agents_manager import AgentsManager, WorkflowBuilder
    print("SUCCESS: Imported AgentsManager and WorkflowBuilder")
except ImportError as e:
    print(f"ERROR: Failed to import from agents_manager module: {e}")

# Test creating an instance
try:
    manager = AgentsManager(app_name="test_app")
    print("SUCCESS: Created AgentsManager instance")
except Exception as e:
    print(f"ERROR: Failed to create AgentsManager instance: {e}")

print("Import test completed!")