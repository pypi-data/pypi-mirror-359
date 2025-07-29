# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-07-01

### Added

- **Enhanced Multicast Messaging**
  - Full LINE API support with all optional parameters
  - `notification_disabled` parameter for silent message sending
  - `custom_aggregation_units` for analytics tracking and campaign management
  - `retry_key` parameter for idempotent message sending
  - Comprehensive error handling and validation
  - Interactive examples with user input for testing

- **Strict Development Guidelines**
  - Comprehensive AI agent instructions with non-negotiable requirements
  - Mandatory type safety, async patterns, and testing standards
  - Quality gates that must pass before code completion
  - Security requirements for credential management
  - Performance standards for async operations

- **Improved Project Structure**
  - Moved documentation to proper `docs/` directory organization
  - Enhanced project structure with clear separation of concerns
  - Better examples with real-world usage scenarios
  - Comprehensive testing patterns and coverage requirements

### Enhanced

- **LineMessagingClient**: Added support for all multicast API parameters
- **Request Models**: Enhanced with notification and analytics options
- **Examples**: Added comprehensive multicast examples with interactive input
- **Documentation**: Updated with new features and usage patterns

### Fixed

- **Project Organization**: Proper documentation structure in `docs/` directory
- **Type Safety**: Enhanced type coverage for all new features
- **Error Handling**: Better error messages and user guidance

## [1.0.0] - 2025-06-30

### Added

- **Complete LINE Messaging API Integration**
  - Push messages, reply messages, multicast, and broadcast functionality
  - Support for text, image, location, sticker, and Flex messages
  - Async-first design with proper error handling and retry logic
  - Rate limiting and connection management

- **Type-Safe Flex Messages**
  - Complete Pydantic models for all Flex Message components
  - FlexBox, FlexBubble, FlexText, FlexImage, FlexButton support
  - FlexCarousel and FlexSeparator components
  - JSON export and clipboard integration for LINE simulator testing
  - Factory methods for easy component creation

- **Comprehensive Webhook Handling**
  - Secure signature verification for webhook authenticity
  - Type-safe event models for all LINE webhook events
  - Decorator-based event handlers for clean code organization
  - Support for message, postback, follow, and unfollow events
  - FastAPI integration examples

- **Production-Ready Features**
  - Full Pydantic integration with comprehensive type hints
  - Automatic environment variable discovery and validation
  - Comprehensive error handling with typed exceptions
  - Built-in retry mechanisms with exponential backoff
  - Structured logging throughout the library

- **Developer Experience**
  - Rich IDE support with full type hints
  - Auto-completion for all API methods
  - Comprehensive test suite with pytest
  - Example code and documentation
  - UV package manager integration

- **Configuration Management**
  - Automatic .env file discovery
  - Environment variable validation
  - Type-safe configuration across all services
  - Secure credential management

### Technical Implementation

- Modern Python 3.9+ with enhanced type hints
- Async/await patterns throughout
- HTTPX for high-performance HTTP operations
- Pydantic 2.x for data validation and settings
- Comprehensive test coverage
- Code quality tools (ruff, mypy)

## [Unreleased]

### To Be Added

- N/A

### To Be Changed

- N/A

### To Be Fixed

- N/A

### To Be Removed

- N/A

### Security Updates

- N/A
