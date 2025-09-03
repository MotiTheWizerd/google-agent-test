"""Session manager for creating and managing agent sessions."""

import uuid
from typing import Optional
from google.adk.sessions import InMemorySessionService
from ...ui.terminal_ui_manager import TerminalUIManager


class SessionManager:
    """Manager for session creation and management."""
    
    def __init__(self, session_service: InMemorySessionService, ui: TerminalUIManager):
        self.session_service = session_service
        self.ui = ui
    
    async def get_or_create_session(self, 
                                  app_name: str, 
                                  user_id: str, 
                                  session_id: Optional[str] = None) -> object:
        """
        Get an existing session or create a new one.
        
        Args:
            app_name: The application name
            user_id: The user ID
            session_id: The session ID (optional, will generate if None)
            
        Returns:
            The session object
        """
        # If no session_id provided, generate a UUID
        if not session_id:
            session_id = str(uuid.uuid4())
        
        session = None
        # Try to get existing session
        try:
            session = await self.session_service.get_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
            self.ui.print_session_creation("Retrieved existing session", session.id if session else None)
            # If session doesn't exist, create a new one
            if session is None:
                self.ui.print_warning("Session not found, creating new one")
                session = await self.session_service.create_session(
                    app_name=app_name,
                    user_id=user_id,
                    session_id=session_id
                )
                self.ui.print_session_creation("Created new session", session.id if session else None)
        except Exception as e:
            # If there's an exception, create a new one
            self.ui.print_warning(f"Session not found or error occurred, creating new one: {e}")
            session = await self.session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
            self.ui.print_session_creation("Created new session", session.id if session else None)
        
        # Check if session was created successfully
        if session is None:
            raise ValueError("Failed to create or retrieve session")
        
        return session