"""Workflow manager for registering and managing agent workflows."""

from typing import Dict, List, Optional
from ...core.agents_manager.agent_types import WorkflowConfig


class WorkflowManager:
    """Manager for workflow registration and management."""
    
    def __init__(self):
        self._workflows: Dict[str, WorkflowConfig] = {}
    
    def register_workflow(self, workflow_config: WorkflowConfig) -> None:
        """Register a workflow configuration."""
        self._workflows[workflow_config.name] = workflow_config
    
    def get_workflow(self, name: str) -> Optional[WorkflowConfig]:
        """Get a workflow configuration by name."""
        return self._workflows.get(name)
    
    def list_workflows(self) -> List[str]:
        """List all registered workflow names."""
        return list(self._workflows.keys())
    
    def workflow_exists(self, name: str) -> bool:
        """Check if a workflow exists."""
        return name in self._workflows