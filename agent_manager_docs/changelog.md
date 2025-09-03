# Changelog

## [Unreleased]

### Fixed
- Fixed session handling in AgentsManager to properly handle cases where `get_session` returns `None` instead of raising an exception
- Updated `InMemorySessionService` initialization to remove invalid `dev_ui` parameter
- Updated runner initialization to use `Runner` instead of `InMemoryRunner` with proper session service parameter

### Added
- Enhanced error handling and debugging output for session creation/retrieval
- Interactive Q&A agent example with improved session management
- Support for custom user IDs and session IDs in interactive examples
- Created separate UI module with TerminalUIManager for handling rich console output
- Separated UI logic from business logic in AgentsManager
- Enhanced TerminalUIManager with rich visual elements, emojis, and animated effects
- Automatic UUID generation for sessions when not provided
- Themed color schemes for different visual styles

### Changed
- Improved session creation logic to handle both existing and new sessions properly
- Updated AgentsManager to use the correct ADK Runner API
- Enhanced interactive agent example with better user experience
- Moved all console output logic to TerminalUIManager
- Updated interactive Q&A agent to use default user ID and automatic session generation
- Removed user input prompts for session ID in interactive examples

## 2025-09-03

### Initial Implementation
- Basic AgentsManager implementation with support for LLM, Sequential, Parallel, and Loop agents
- Workflow builder pattern for creating complex agent workflows
- Tool registration system for extending agent capabilities
- Multi-user session management with proper isolation