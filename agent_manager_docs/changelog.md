# Changelog

## [Unreleased]

### Fixed
- Fixed session handling in AgentsManager to properly handle cases where `get_session` returns `None` instead of raising an exception
- Updated `InMemorySessionService` initialization to remove invalid `dev_ui` parameter
- Updated runner initialization to use `Runner` instead of `InMemoryRunner` with proper session service parameter
- **Streaming Fix**: Enabled proper streaming in Google ADK by adding RunConfig with StreamingMode.SSE
- **Streaming Fix**: Fixed event handling to properly process partial responses and final responses
- **Streaming Fix**: Added console flushing to ensure real-time output display
- **Encoding Fix**: Added Unicode encoding error handling to prevent issues with emojis on Windows
- **Mem0 API Compatibility**: Updated Mem0 adapter to work with the latest Mem0 client API, including proper method names and parameter formats

### Added
- Enhanced error handling and debugging output for session creation/retrieval
- Interactive Q&A agent example with improved session management
- Support for custom user IDs and session IDs in interactive examples
- Created separate UI module with TerminalUIManager for handling rich console output
- Separated UI logic from business logic in AgentsManager
- **Modular Architecture**: Refactored AgentsManager into smaller, focused modules:
  - WorkflowManager for workflow registration and management
  - SessionManager for session creation and management
  - RunnerManager for runner creation and management
  - WorkflowExecutor for workflow execution orchestration
- **Streaming Support**: Added streaming functionality to AgentsManager:
  - `stream_workflow` method in AgentsManager for real-time event processing
  - `stream_workflow` method in WorkflowExecutor for handling ADK event streaming
  - Streaming example demonstrating real-time response processing
  - Updated documentation with streaming usage examples and best practices
- **Memory Module**: Added comprehensive memory integration module:
  - Stable interface with Protocol and TypedDict definitions
  - Mem0 adapter with proper error handling and retry logic
  - Configuration management with environment variable support
  - Comprehensive test suite with mocked clients
  - Integration examples with the Agents Manager
- **Enhanced Streaming**: Improved streaming implementation with proper real-time output:
  - Added proper handling of partial responses for streaming text output
  - Enhanced UI manager with streaming text support
  - Improved event processing to properly support real-time output streaming
  - Added streaming test scripts to verify functionality

### Changed
- Improved session creation logic to handle both existing and new sessions properly
- Updated AgentsManager to use the correct ADK Runner API
- Enhanced interactive agent example with better user experience
- Moved all console output logic to TerminalUIManager
- **Refactored AgentsManager** to coordinate between specialized modules instead of handling all responsibilities directly
- **Improved Streaming**: Enhanced event handling to properly support real-time output streaming with better UI integration

## 2025-09-03

### Initial Implementation
- Basic AgentsManager implementation with support for LLM, Sequential, Parallel, and Loop agents
- Workflow builder pattern for creating complex agent workflows
- Tool registration system for extending agent capabilities
- Multi-user session management with proper isolation